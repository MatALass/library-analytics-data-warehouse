"""
Generateur de donnees - Library Analytics Data Warehouse
=========================================================

Modele : constellation (3 tables de faits + 5 dimensions partagees).

    FACT_LOAN                 (grain : 1 emprunt)
    FACT_RESERVATION          (grain : 1 reservation)
    FACT_INVENTORY_SNAPSHOT   (grain : 1 etat de stock livre x branche x mois)

Objectif specifique : les donnees ne sont PAS uniformes. Des tendances sont
injectees volontairement et de maniere correlee pour que l'analyse Power BI
revele des signaux exploitables (cf. 05_documentation/PATTERNS_ANALYTIQUES.md).

Les dimensions sont reprises telles quelles depuis le dossier source, a
l'exception de DIM_BOOK dont on retire les colonnes d'inventaire (ce sont des
faits, pas des attributs : ils vivent desormais dans FACT_INVENTORY_SNAPSHOT).

Reproductible : seed fixe. Aucune dependance hors pandas / numpy.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
rng = np.random.default_rng(SEED)

HERE = Path(__file__).resolve().parent
DIMS_SRC = HERE / "source_dimensions"          # dimensions sources (hand-authored)
OUT = HERE.parent / "01_data_csv"             # sortie CSV
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# 0. Chargement des dimensions source
# ----------------------------------------------------------------------------
def read_dim(name: str) -> pd.DataFrame:
    return pd.read_csv(DIMS_SRC / f"{name}.csv", dtype=str, keep_default_na=False,
                       na_values=[""]).rename(columns=lambda c: c.lstrip("\ufeff"))

dim_date = read_dim("DIM_DATE")
dim_cat = read_dim("DIM_CATEGORY")
dim_branch = read_dim("DIM_BRANCH")
dim_user = read_dim("DIM_USER")
dim_book = read_dim("DIM_BOOK")

# DIM_BOOK nettoye : on garde uniquement les attributs livre.
BOOK_ATTR = ["book_id", "isbn", "title", "author", "category_id", "category",
             "genre", "academic_level", "language", "publication_year",
             "demand_tier", "base_total_copies", "popularity_score"]
dim_book = dim_book[BOOK_ATTR].copy()

# Index pratiques
dim_date["dt"] = pd.to_datetime(dim_date["full_date"])
dim_date["is_exam"] = dim_date["is_exam_period"].eq("True")
dim_date["is_weekend_b"] = dim_date["is_weekend"].eq("True")
dim_date = dim_date.sort_values("dt").reset_index(drop=True)

book_cat = dict(zip(dim_book["book_id"], dim_book["category_id"]))
book_tier = dict(zip(dim_book["book_id"], dim_book["demand_tier"]))
book_base_copies = dict(zip(dim_book["book_id"], dim_book["base_total_copies"].astype(int)))
book_level = dict(zip(dim_book["book_id"], dim_book["academic_level"]))
books_by_cat: dict[str, list[str]] = {}
for bid, cid in book_cat.items():
    books_by_cat.setdefault(cid, []).append(bid)

# ----------------------------------------------------------------------------
# 1. Parametres de tendance (le coeur du "non-uniforme")
# ----------------------------------------------------------------------------

# 1a. Poids de demande par livre -> genere le Pareto 80/20.
TIER_WEIGHT = {"top": 6.0, "high": 3.0, "medium": 1.2, "low": 0.45}
book_demand = {}
for bid in dim_book["book_id"]:
    w = TIER_WEIGHT[book_tier[bid]]
    # jitter lognormal : de la dispersion meme a l'interieur d'un tier
    book_demand[bid] = w * float(rng.lognormal(0.0, 0.45))

# 1b. Charge globale d'emprunts par branche (volume).
BRANCH_LOAD = {"1": 1.00, "2": 0.80, "3": 0.42, "4": 0.50, "5": 0.78, "6": 0.32}

# 1c. Tension de stock par branche (sous/sur-allocation vs demande).
#     >1 = branche tendue (rupture probable), <1 = branche avec stock dormant.
BRANCH_TENSION = {"1": 1.28, "2": 1.00, "3": 0.62, "4": 1.12, "5": 1.25, "6": 0.55}

# 1d. Sensibilite aux examens par categorie (multiplicateur en periode d'exam).
#     STEM / Droit / Sante / Eco montent fort ; Lettres / SHS restent plats.
CAT_EXAM = {"1": 1.9, "2": 1.7, "3": 1.6, "4": 1.8, "5": 2.1,
            "6": 2.0, "7": 1.6, "8": 1.05, "9": 0.95}

# 1e. Affinite faculte usager -> categorie (proba relative d'emprunt).
FACULTY_AFFINITY = {
    "Informatique":     {"1": 4, "2": 4, "3": 4, "4": 3, "5": .3, "6": .3, "7": 1, "8": .5, "9": .5},
    "Droit":            {"1": .3, "2": .4, "3": .2, "4": .6, "5": 6, "6": .5, "7": 1.2, "8": 1.5, "9": .8},
    "Médecine":         {"1": .8, "2": .4, "3": .3, "4": 2, "5": .6, "6": 6, "7": .5, "8": .8, "9": .4},
    "Économie-Gestion": {"1": 1, "2": 2.5, "3": .6, "4": 2, "5": 1, "6": .4, "7": 5, "8": .8, "9": .5},
    "Lettres":          {"1": .2, "2": .2, "3": .1, "4": .3, "5": .6, "6": .3, "7": .5, "8": 2, "9": 6},
    "Sciences Humaines":{"1": .3, "2": .3, "3": .2, "4": .8, "5": 1.5, "6": .8, "7": .8, "8": 5, "9": 2.5},
}

# 1f. Activite par usager (power-law) : quelques gros emprunteurs.
USERTYPE_BASE = {"Student": 1.0, "Researcher": 2.2, "Faculty": 2.6}
user_activity = {}
for _, u in dim_user.iterrows():
    if u["is_active"] != "True":
        user_activity[u["user_id"]] = 0.0
        continue
    base = USERTYPE_BASE.get(u["user_type"], 1.0)
    user_activity[u["user_id"]] = base * float(rng.lognormal(0.0, 0.7))
user_meta = dim_user.set_index("user_id").to_dict("index")

# 1g. Politique de pret (jours autorises) et propension au retard.
LOAN_PERIOD = {"Student": 14, "Researcher": 28, "Faculty": 28}
LATE_PRONE = {"Student": 0.22, "Researcher": 0.14, "Faculty": 0.12}

# ----------------------------------------------------------------------------
# 2. Profil temporel : intensite d'emprunt par jour
# ----------------------------------------------------------------------------
def day_intensity(row) -> float:
    f = 1.0
    if row["is_weekend_b"]:
        f *= 0.35
    period = row["academic_period"]
    if period == "Examens":
        f *= 2.4
    elif period == "Rentrée":
        f *= 1.5
    elif period == "Vacances été":
        f *= 0.30
    # tendance annuelle : reseau en croissance
    year = int(row["year"])
    f *= {2024: 0.85, 2025: 1.00, 2026: 1.15}.get(year, 1.0)
    return f

dim_date["intensity"] = dim_date.apply(day_intensity, axis=1)

# ----------------------------------------------------------------------------
# 3. FACT_LOAN
# ----------------------------------------------------------------------------
N_LOANS = 16000
date_rows = dim_date.to_dict("records")
date_p = np.array([r["intensity"] for r in date_rows], dtype=float)
date_p /= date_p.sum()

user_ids = list(user_activity.keys())
user_p = np.array([user_activity[u] for u in user_ids], dtype=float)
user_p /= user_p.sum()

branch_ids = list(BRANCH_LOAD.keys())
branch_p = np.array([BRANCH_LOAD[b] for b in branch_ids], dtype=float)
branch_p /= branch_p.sum()

# Croissance specifique Bruxelles (5) : monte plus vite dans le temps.
def branch_pick(user_pref: str, year: int) -> str:
    # 65% branche preferee, sinon tirage pondere par la charge
    if rng.random() < 0.65 and user_pref in BRANCH_LOAD:
        return user_pref
    p = branch_p.copy()
    boost = {2024: 0.8, 2025: 1.2, 2026: 1.6}.get(year, 1.0)
    p[branch_ids.index("5")] *= boost      # Bruxelles accelere
    p /= p.sum()
    return rng.choice(branch_ids, p=p)

# Pre-calcul des vecteurs de proba categorie par (faculte, exam)
cat_ids = list(books_by_cat.keys())
def cat_vector(faculty: str, exam: bool) -> np.ndarray:
    aff = FACULTY_AFFINITY.get(faculty, {c: 1 for c in cat_ids})
    v = np.array([aff.get(c, 1.0) * (CAT_EXAM[c] if exam else 1.0) for c in cat_ids])
    return v / v.sum()

# poids livre normalises par categorie (pour Pareto intra-categorie)
book_p_by_cat = {c: np.array([book_demand[b] for b in books_by_cat[c]]) for c in cat_ids}
for c in cat_ids:
    book_p_by_cat[c] = book_p_by_cat[c] / book_p_by_cat[c].sum()

loan_date_idx = rng.choice(len(date_rows), size=N_LOANS, p=date_p)
loan_users = rng.choice(user_ids, size=N_LOANS, p=user_p)

loans = []
for i in range(N_LOANS):
    dr = date_rows[loan_date_idx[i]]
    uid = loan_users[i]
    um = user_meta[uid]
    year = int(dr["year"])
    branch = branch_pick(um["preferred_branch_id"], year)
    # categorie puis livre
    cvec = cat_vector(um["faculty"], dr["is_exam"])
    cid = rng.choice(cat_ids, p=cvec)
    bid = rng.choice(books_by_cat[cid], p=book_p_by_cat[cid])

    loan_dt = dr["dt"]
    period = LOAN_PERIOD.get(um["user_type"], 14)
    due_dt = loan_dt + pd.Timedelta(days=period)

    # retour : retard correle a la propension + stress d'examen
    late_prob = LATE_PRONE.get(um["user_type"], 0.2) * (1.5 if dr["is_exam"] else 1.0)
    if rng.random() < late_prob:
        overdue = int(rng.integers(1, 22))
    else:
        overdue = 0
    # certains retours en avance, sinon autour de la date prevue
    early = int(rng.integers(0, 5)) if rng.random() < 0.4 else 0
    return_dt = due_dt + pd.Timedelta(days=overdue) - pd.Timedelta(days=early)

    # emprunts recents encore en cours -> pas de retour
    max_dt = dim_date["dt"].max()
    if return_dt > max_dt:
        return_dt = pd.NaT
        overdue = 0
        duration = (max_dt - loan_dt).days
    else:
        duration = (return_dt - loan_dt).days
    duration = max(duration, 1)

    penalty = round(overdue * 0.30, 2) if overdue > 0 else 0.0

    loans.append({
        "date_id": dr["date_id"],
        "event_date": dr["full_date"],
        "user_id": uid,
        "book_id": bid,
        "branch_id": branch,
        "category_id": cid,
        "loan_date": loan_dt.strftime("%Y-%m-%d"),
        "due_date": due_dt.strftime("%Y-%m-%d"),
        "return_date": return_dt.strftime("%Y-%m-%d") if pd.notna(return_dt) else "",
        "loan_duration_days": duration,
        "days_overdue": overdue,
        "penalty_amount": penalty,
        "quantity": 1,
    })

fact_loan = pd.DataFrame(loans)
fact_loan.insert(0, "loan_id", ["L%06d" % (i + 1) for i in range(len(fact_loan))])

# ----------------------------------------------------------------------------
# 4. FACT_RESERVATION
#    Plus de reservations sur livres demandes en branches tendues + plus
#    d'attente / d'annulations la ou ca coince.
# ----------------------------------------------------------------------------
N_RES = 3600
res_date_idx = rng.choice(len(date_rows), size=N_RES, p=date_p)
res_users = rng.choice(user_ids, size=N_RES, p=user_p)

reservations = []
for i in range(N_RES):
    dr = date_rows[res_date_idx[i]]
    uid = res_users[i]
    um = user_meta[uid]
    year = int(dr["year"])
    branch = branch_pick(um["preferred_branch_id"], year)
    cvec = cat_vector(um["faculty"], dr["is_exam"])
    cid = rng.choice(cat_ids, p=cvec)
    bid = rng.choice(books_by_cat[cid], p=book_p_by_cat[cid])

    # pression = demande livre x tension branche x examens
    tension = BRANCH_TENSION[branch] * (1.4 if dr["is_exam"] else 1.0)
    demand_norm = min(book_demand[bid] / 3.0, 2.5)
    pressure = tension * (0.6 + 0.4 * demand_norm)

    # statut : plus de pression -> moins de fulfilled, plus de pending/cancelled
    p_fulfilled = float(np.clip(0.85 - 0.35 * (pressure - 1.0), 0.30, 0.92))
    p_cancel = float(np.clip(0.06 + 0.18 * (pressure - 1.0), 0.04, 0.40))
    p_pending = max(0.02, 1 - p_fulfilled - p_cancel)
    status = rng.choice(["fulfilled", "pending", "cancelled"],
                        p=np.array([p_fulfilled, p_pending, p_cancel]) /
                          (p_fulfilled + p_pending + p_cancel))

    # attente : forte la ou ca coince
    base_wait = rng.gamma(shape=2.0, scale=2.5 * pressure)
    wait = 0 if status == "fulfilled" and pressure < 1.0 else int(round(base_wait))
    wait = min(wait, 45)

    reservations.append({
        "date_id": dr["date_id"],
        "event_date": dr["full_date"],
        "user_id": uid,
        "book_id": bid,
        "branch_id": branch,
        "category_id": cid,
        "reservation_status": status,
        "wait_days": wait,
        "quantity": 1,
    })

fact_res = pd.DataFrame(reservations)
fact_res.insert(0, "reservation_id", ["R%06d" % (i + 1) for i in range(len(fact_res))])

# ----------------------------------------------------------------------------
# 5. FACT_INVENTORY_SNAPSHOT  (snapshot periodique mensuel, fin de mois)
#    C'est ici que vit l'histoire de reallocation.
# ----------------------------------------------------------------------------
# allocation copies par livre x branche : on sous-alloue les branches tendues
# et on sur-alloue les branches dormantes -> desequilibre volontaire.
ALLOC_WEIGHT = {"1": 0.85, "2": 1.00, "3": 1.35, "4": 0.80, "5": 0.85, "6": 1.45}
alloc = {}
for bid in dim_book["book_id"]:
    total = book_base_copies[bid]
    raw = np.array([ALLOC_WEIGHT[b] * BRANCH_LOAD[b] for b in branch_ids])
    raw = raw / raw.sum()
    copies = np.maximum(1, np.round(total * raw)).astype(int)
    for b, c in zip(branch_ids, copies):
        alloc[(bid, b)] = int(c)

# loans agreges par livre x branche x mois (pour loan_count_120d / total)
fl = fact_loan.copy()
fl["ym"] = fl["loan_date"].str.slice(0, 7)
fl["ld"] = pd.to_datetime(fl["loan_date"])
loan_count_cum = {}        # cumul jusqu'au mois inclus
loan_count_120 = {}        # fenetre 120j avant fin de mois

# dates de snapshot : dernier jour disponible de chaque mois present
months = sorted(dim_date["year_month"].unique())
month_last = {}
for ym in months:
    sub = dim_date[dim_date["year_month"] == ym]
    month_last[ym] = sub.iloc[-1]  # derniere date du mois dans le calendrier

SEASON = {"Examens": 1.30, "Rentrée": 1.12, "Vacances été": 0.50, "Hors examens": 1.0}
TIER_UTIL = {"top": 1.10, "high": 0.92, "medium": 0.68, "low": 0.40}

def priority(util_target: float) -> str:
    if util_target >= 1.15:
        return "Critique"
    if util_target >= 1.00:
        return "Élevée"
    if util_target >= 0.75:
        return "Normale"
    return "Faible"

snap_rows = []
for ym in months:
    drow = month_last[ym]
    snap_date = drow["full_date"]
    snap_dt = drow["dt"]
    season = SEASON.get(drow["academic_period"], 1.0)
    exam = drow["is_exam"]
    win_start = snap_dt - pd.Timedelta(days=120)

    for bid in dim_book["book_id"]:
        cid = book_cat[bid]
        exam_mult = (CAT_EXAM[cid] / 1.8) if exam else 1.0   # normalise l'effet exam
        base_u = TIER_UTIL[book_tier[bid]] * (0.85 + 0.30 * (book_demand[bid] / 3.0))
        for b in branch_ids:
            total = alloc[(bid, b)]
            util_target = base_u * BRANCH_TENSION[b] * season * exam_mult
            util_target = float(np.clip(util_target * rng.normal(1.0, 0.08), 0.05, 1.8))

            active = int(round(min(1.0, util_target) * total))
            active = min(active, total)
            available = total - active
            out_of_stock = available == 0
            unsatisfied = int(round(max(0.0, util_target - 1.0) * total))

            # comptes d'emprunts reels sur ce livre x branche
            mask_b = (fl["book_id"] == bid) & (fl["branch_id"] == b)
            cum = int(((fl["ld"] <= snap_dt) & mask_b).sum())
            w120 = int(((fl["ld"] > win_start) & (fl["ld"] <= snap_dt) & mask_b).sum())

            util_rate = round(active / total, 4) if total else 0.0
            avail_rate = round(available / total, 4) if total else 0.0

            snap_rows.append({
                "date_id": drow["date_id"],
                "snapshot_date": snap_date,
                "book_id": bid,
                "branch_id": b,
                "category_id": cid,
                "total_copies": total,
                "available_copies": available,
                "active_loans": active,
                "utilization_rate": util_rate,
                "availability_rate": avail_rate,
                "out_of_stock": out_of_stock,
                "loan_count_total": cum,
                "loan_count_120d": w120,
                "unsatisfied_reservations": unsatisfied,
                "reallocation_priority": priority(util_target),
            })

fact_snap = pd.DataFrame(snap_rows)
fact_snap.insert(0, "snapshot_id", ["S%07d" % (i + 1) for i in range(len(fact_snap))])

# ----------------------------------------------------------------------------
# 6. Ecriture (UTF-8 sans BOM, types entiers propres)
# ----------------------------------------------------------------------------
def write(df: pd.DataFrame, name: str):
    df.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8")
    print(f"  {name:28s} {df.shape[0]:>7} lignes x {df.shape[1]} cols")

print("Ecriture des CSV ->", OUT)
write(dim_date.drop(columns=["dt", "is_exam", "is_weekend_b", "intensity"]), "DIM_DATE")
write(dim_cat, "DIM_CATEGORY")
write(dim_branch, "DIM_BRANCH")
write(dim_user, "DIM_USER")
write(dim_book, "DIM_BOOK")
write(fact_loan, "FACT_LOAN")
write(fact_res, "FACT_RESERVATION")
write(fact_snap, "FACT_INVENTORY_SNAPSHOT")
print("OK.")
