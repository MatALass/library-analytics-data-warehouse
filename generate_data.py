from __future__ import annotations
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIMS_SRC = HERE / "source_dimensions"                
DEFAULT_OUT = HERE / "data"   

PRIORITY = {"Critique": "Critical", "Élevée": "High", "Normale": "Normal", "Faible": "Low"}
ACADEMIC_PERIOD = {"Examens": "Exams", "Hors examens": "Off-Exam", "Rentrée": "Back-to-School", "Vacances été": "Summer Break"}
MONTH = {"Janvier": "January", "Février": "February", "Mars": "March", "Avril": "April", "Mai": "May", "Juin": "June", "Juillet": "July", "Août": "August", "Septembre": "September", 
         "Octobre": "October", "Novembre": "November", "Décembre": "December"}
CATEGORY = {"Data Science & IA": "Data Science & AI", "Droit": "Law", "Santé": "Health", "Sciences Humaines": "Humanities", "Littérature": "Literature",
             "Économie-Gestion": "Economics & Management", "Statistiques": "Statistics"}
DISCIPLINE = {"Numérique": "Digital", "Sciences sociales": "Social Sciences", "Santé": "Health", "Gestion": "Management", "Lettres": "Letters"}
SUBCATEGORY = {"Droit public / privé": "Public / Private Law", "Médecine / Santé publique": "Medicine / Public Health", "Sociologie / Psychologie": "Sociology / Psychology",
               "Romans / essais": "Novels / Essays", "Analyse quantitative": "Quantitative Analysis"}
FACULTY = {"Droit": "Law", "Informatique": "Computer Science", "Lettres": "Humanities",
           "Médecine": "Medicine", "Sciences Humaines": "Social Sciences",
           "Économie-Gestion": "Economics & Management"}
BRANCH_TYPE = {"Université": "University", "École": "School"}          
COUNTRY = {"Belgique": "Belgium"}                                      
CITY = {"Bruxelles": "Brussels"}                                    
BRANCH_NAME = {"Bibliothèque Paris-Centre": "Paris-Centre Library", "Campus LyonTech": "LyonTech Campus", "IUT Lille Médiathèque": "Lille IUT Media Library",
               "BUT Marseille Bibliothèque": "Marseille BUT Library", "ULB Bruxelles Sciences": "ULB Brussels Sciences", "Campus Liège Recherche": "Liège Research Campus"}
BRANCH_PROFILE = {"Très forte activité : étudiants data/droit": "Very high activity: data/law students", "Forte activité : engineering et BI": "High activity: engineering and BI",
                  "Activité moyenne : BUT/IUT": "Medium activity: BUT/IUT", "Faible disponibilité sur ouvrages pratiques": "Low availability on practical books",
                  "Très forte activité : recherche et santé": "Very high activity: research and health", "Activité recherche spécialisée": "Specialised research activity"}
DEPARTMENT = {"Bruxelles-Capitale": "Brussels-Capital", "Wallonie": "Wallonia"}  
TRANSLATIONS = {
    "DIM_DATE":   {"academic_period": ACADEMIC_PERIOD, "month_name": MONTH},
    "DIM_CATEGORY": {"category": CATEGORY, "discipline_cluster": DISCIPLINE, "subcategory": SUBCATEGORY},
    "DIM_BOOK":   {"category": CATEGORY},
    "DIM_USER":   {"faculty": FACULTY, "country": COUNTRY},
    "DIM_BRANCH": {"branch_type": BRANCH_TYPE, "country": COUNTRY, "city": CITY, "branch_name": BRANCH_NAME, "branch_profile": BRANCH_PROFILE, "department": DEPARTMENT},
    "FACT_INVENTORY_SNAPSHOT": {"reallocation_priority": PRIORITY},
}


def translate_df(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Apply the FR->EN maps for `name` in place (returns df)."""
    for col, m in TRANSLATIONS.get(name, {}).items():
        if col in df.columns:
            df[col] = df[col].map(lambda v: m.get(v, v))
    return df


def read_dim(name: str) -> pd.DataFrame:
    return pd.read_csv(DIMS_SRC / f"{name}.csv", dtype=str, keep_default_na=False,
                       na_values=[""]).rename(columns=lambda c: c.lstrip("\ufeff"))


def build(seed: int):
    rng = np.random.default_rng(seed)
    dim_date = read_dim("DIM_DATE")
    dim_cat = read_dim("DIM_CATEGORY")
    dim_branch = read_dim("DIM_BRANCH")
    dim_user = read_dim("DIM_USER")
    dim_book = read_dim("DIM_BOOK")
    BOOK_ATTR = ["book_id", "isbn", "title", "author", "category_id", "category", "genre", "academic_level", "language", 
                 "publication_year", "demand_tier", "base_total_copies", "popularity_score"]
    dim_book = dim_book[BOOK_ATTR].copy()
    dim_date["dt"] = pd.to_datetime(dim_date["full_date"])
    dim_date["is_exam"] = dim_date["is_exam_period"].eq("True")
    dim_date["is_weekend_b"] = dim_date["is_weekend"].eq("True")
    dim_date = dim_date.sort_values("dt").reset_index(drop=True)
    book_cat = dict(zip(dim_book["book_id"], dim_book["category_id"]))
    book_tier = dict(zip(dim_book["book_id"], dim_book["demand_tier"]))
    book_base_copies = dict(zip(dim_book["book_id"], dim_book["base_total_copies"].astype(int)))
    books_by_cat: dict[str, list[str]] = {}
    for bid, cid in book_cat.items():
        books_by_cat.setdefault(cid, []).append(bid)

    TIER_WEIGHT = {"top": 6.0, "high": 3.0, "medium": 1.2, "low": 0.45}
    book_demand = {bid: TIER_WEIGHT[book_tier[bid]] * float(rng.lognormal(0.0, 0.45)) for bid in dim_book["book_id"]}
    BRANCH_LOAD = {"1": 1.00, "2": 0.80, "3": 0.42, "4": 0.50, "5": 0.78, "6": 0.32}
    BRANCH_TENSION = {"1": 1.28, "2": 1.00, "3": 0.62, "4": 1.12, "5": 1.25, "6": 0.55}
    CAT_EXAM = {"1": 1.9, "2": 1.7, "3": 1.6, "4": 1.8, "5": 2.1, "6": 2.0, "7": 1.6, "8": 1.05, "9": 0.95}
    FACULTY_AFFINITY = {
        "Informatique":     {"1": 4, "2": 4, "3": 4, "4": 3, "5": .3, "6": .3, "7": 1, "8": .5, "9": .5},
        "Droit":            {"1": .3, "2": .4, "3": .2, "4": .6, "5": 6, "6": .5, "7": 1.2, "8": 1.5, "9": .8},
        "Médecine":         {"1": .8, "2": .4, "3": .3, "4": 2, "5": .6, "6": 6, "7": .5, "8": .8, "9": .4},
        "Économie-Gestion": {"1": 1, "2": 2.5, "3": .6, "4": 2, "5": 1, "6": .4, "7": 5, "8": .8, "9": .5},
        "Lettres":          {"1": .2, "2": .2, "3": .1, "4": .3, "5": .6, "6": .3, "7": .5, "8": 2, "9": 6},
        "Sciences Humaines":{"1": .3, "2": .3, "3": .2, "4": .8, "5": 1.5, "6": .8, "7": .8, "8": 5, "9": 2.5},
    }
    USERTYPE_BASE = {"Student": 1.0, "Researcher": 2.2, "Faculty": 2.6}
    user_activity = {}
    for _, u in dim_user.iterrows():
        user_activity[u["user_id"]] = 0.0 if u["is_active"] != "True" \
            else USERTYPE_BASE.get(u["user_type"], 1.0) * float(rng.lognormal(0.0, 0.7))
    user_meta = dim_user.set_index("user_id").to_dict("index")
    LOAN_PERIOD = {"Student": 14, "Researcher": 28, "Faculty": 28}
    LATE_PRONE = {"Student": 0.22, "Researcher": 0.14, "Faculty": 0.12}

    def day_intensity(row) -> float:
        f = 1.0
        if row["is_weekend_b"]:
            f *= 0.35
        period = row["academic_period"]
        f *= {"Examens": 2.4, "Rentrée": 1.5, "Vacances été": 0.30}.get(period, 1.0)
        f *= {"2024": 0.85, "2025": 1.00, "2026": 1.15}.get(str(row["year"]), 1.0)
        return f

    dim_date["intensity"] = dim_date.apply(day_intensity, axis=1)
    N_LOANS = 16000
    date_rows = dim_date.to_dict("records")
    date_p = np.array([r["intensity"] for r in date_rows], dtype=float); date_p /= date_p.sum()
    user_ids = list(user_activity.keys())
    user_p = np.array([user_activity[u] for u in user_ids], dtype=float); user_p /= user_p.sum()
    branch_ids = list(BRANCH_LOAD.keys())
    branch_p = np.array([BRANCH_LOAD[b] for b in branch_ids], dtype=float); branch_p /= branch_p.sum()

    def branch_pick(user_pref: str, year: int) -> str:
        if rng.random() < 0.65 and user_pref in BRANCH_LOAD:
            return user_pref
        p = branch_p.copy()
        p[branch_ids.index("5")] *= {2024: 0.8, 2025: 1.2, 2026: 1.6}.get(year, 1.0)  # Brussels accelerates
        p /= p.sum()
        return rng.choice(branch_ids, p=p)

    cat_ids = list(books_by_cat.keys())

    def cat_vector(faculty: str, exam: bool) -> np.ndarray:
        aff = FACULTY_AFFINITY.get(faculty, {c: 1 for c in cat_ids})
        v = np.array([aff.get(c, 1.0) * (CAT_EXAM[c] if exam else 1.0) for c in cat_ids])
        return v / v.sum()

    book_p_by_cat = {c: np.array([book_demand[b] for b in books_by_cat[c]]) for c in cat_ids}
    for c in cat_ids:
        book_p_by_cat[c] = book_p_by_cat[c] / book_p_by_cat[c].sum()

    loan_date_idx = rng.choice(len(date_rows), size=N_LOANS, p=date_p)
    loan_users = rng.choice(user_ids, size=N_LOANS, p=user_p)
    max_dt = dim_date["dt"].max()

    loans = []
    for i in range(N_LOANS):
        dr = date_rows[loan_date_idx[i]]; uid = loan_users[i]; um = user_meta[uid]
        year = int(dr["year"]); branch = branch_pick(um["preferred_branch_id"], year)
        cid = rng.choice(cat_ids, p=cat_vector(um["faculty"], dr["is_exam"]))
        bid = rng.choice(books_by_cat[cid], p=book_p_by_cat[cid])
        loan_dt = dr["dt"]; due_dt = loan_dt + pd.Timedelta(days=LOAN_PERIOD.get(um["user_type"], 14))
        late_prob = LATE_PRONE.get(um["user_type"], 0.2) * (1.5 if dr["is_exam"] else 1.0)
        overdue = int(rng.integers(1, 22)) if rng.random() < late_prob else 0
        early = int(rng.integers(0, 5)) if rng.random() < 0.4 else 0
        return_dt = due_dt + pd.Timedelta(days=overdue) - pd.Timedelta(days=early)
        if return_dt > max_dt:
            return_dt = pd.NaT; overdue = 0; duration = (max_dt - loan_dt).days
        else:
            duration = (return_dt - loan_dt).days
        duration = max(duration, 1)
        loans.append({
            "date_id": dr["date_id"], "event_date": dr["full_date"], "user_id": uid,
            "book_id": bid, "branch_id": branch, "category_id": cid,
            "loan_date": loan_dt.strftime("%Y-%m-%d"), "due_date": due_dt.strftime("%Y-%m-%d"),
            "return_date": return_dt.strftime("%Y-%m-%d") if pd.notna(return_dt) else "",
            "loan_duration_days": duration, "days_overdue": overdue,
            "penalty_amount": round(overdue * 0.30, 2) if overdue > 0 else 0.0, "quantity": 1,
        })
    fact_loan = pd.DataFrame(loans)
    fact_loan.insert(0, "loan_id", ["L%06d" % (i + 1) for i in range(len(fact_loan))])
    N_RES = 3600
    res_date_idx = rng.choice(len(date_rows), size=N_RES, p=date_p)
    res_users = rng.choice(user_ids, size=N_RES, p=user_p)
    reservations = []
    for i in range(N_RES):
        dr = date_rows[res_date_idx[i]]; uid = res_users[i]; um = user_meta[uid]
        year = int(dr["year"]); branch = branch_pick(um["preferred_branch_id"], year)
        cid = rng.choice(cat_ids, p=cat_vector(um["faculty"], dr["is_exam"]))
        bid = rng.choice(books_by_cat[cid], p=book_p_by_cat[cid])
        tension = BRANCH_TENSION[branch] * (1.4 if dr["is_exam"] else 1.0)
        pressure = tension * (0.6 + 0.4 * min(book_demand[bid] / 3.0, 2.5))
        p_fulfilled = float(np.clip(0.85 - 0.35 * (pressure - 1.0), 0.30, 0.92))
        p_cancel = float(np.clip(0.06 + 0.18 * (pressure - 1.0), 0.04, 0.40))
        p_pending = max(0.02, 1 - p_fulfilled - p_cancel)
        status = rng.choice(["fulfilled", "pending", "cancelled"], p=np.array([p_fulfilled, p_pending, p_cancel]) / (p_fulfilled + p_pending + p_cancel))
        base_wait = rng.gamma(shape=2.0, scale=2.5 * pressure)
        wait = 0 if status == "fulfilled" and pressure < 1.0 else int(round(base_wait))
        reservations.append({
            "date_id": dr["date_id"], "event_date": dr["full_date"], "user_id": uid,
            "book_id": bid, "branch_id": branch, "category_id": cid,
            "reservation_status": status, "wait_days": min(wait, 45), "quantity": 1,
        })
    fact_res = pd.DataFrame(reservations)
    fact_res.insert(0, "reservation_id", ["R%06d" % (i + 1) for i in range(len(fact_res))])
    ALLOC_WEIGHT = {"1": 0.85, "2": 1.00, "3": 1.35, "4": 0.80, "5": 0.85, "6": 1.45}
    alloc = {}
    for bid in dim_book["book_id"]:
        raw = np.array([ALLOC_WEIGHT[b] * BRANCH_LOAD[b] for b in branch_ids]); raw /= raw.sum()
        copies = np.maximum(1, np.round(book_base_copies[bid] * raw)).astype(int)
        for b, c in zip(branch_ids, copies):
            alloc[(bid, b)] = int(c)

    fl = fact_loan.copy()
    fl["ld"] = pd.to_datetime(fl["loan_date"])
    months = sorted(dim_date["year_month"].unique())
    month_last = {ym: dim_date[dim_date["year_month"] == ym].iloc[-1] for ym in months}
    SEASON = {"Examens": 1.30, "Rentrée": 1.12, "Vacances été": 0.50, "Hors examens": 1.0}
    TIER_UTIL = {"top": 1.10, "high": 0.92, "medium": 0.68, "low": 0.40}

    def priority(util_target: float) -> str:
        if util_target >= 1.15: return "Critique"
        if util_target >= 1.00: return "Élevée"
        if util_target >= 0.75: return "Normale"
        return "Faible"

    snap_rows = []
    for ym in months:
        drow = month_last[ym]; snap_dt = drow["dt"]
        season = SEASON.get(drow["academic_period"], 1.0); exam = drow["is_exam"]
        win_start = snap_dt - pd.Timedelta(days=120)
        for bid in dim_book["book_id"]:
            cid = book_cat[bid]
            exam_mult = (CAT_EXAM[cid] / 1.8) if exam else 1.0
            base_u = TIER_UTIL[book_tier[bid]] * (0.85 + 0.30 * (book_demand[bid] / 3.0))
            for b in branch_ids:
                total = alloc[(bid, b)]
                util_target = base_u * BRANCH_TENSION[b] * season * exam_mult
                util_target = float(np.clip(util_target * rng.normal(1.0, 0.08), 0.05, 1.8))
                active = min(int(round(min(1.0, util_target) * total)), total)
                available = total - active
                unsatisfied = int(round(max(0.0, util_target - 1.0) * total))
                mask_b = (fl["book_id"] == bid) & (fl["branch_id"] == b)
                cum = int(((fl["ld"] <= snap_dt) & mask_b).sum())
                w120 = int(((fl["ld"] > win_start) & (fl["ld"] <= snap_dt) & mask_b).sum())
                snap_rows.append({
                    "date_id": drow["date_id"], "snapshot_date": drow["full_date"],
                    "book_id": bid, "branch_id": b, "category_id": cid,
                    "total_copies": total, "available_copies": available, "active_loans": active,
                    "utilization_rate": round(active / total, 4) if total else 0.0,
                    "availability_rate": round(available / total, 4) if total else 0.0,
                    "out_of_stock": available == 0, "loan_count_total": cum,
                    "loan_count_120d": w120, "unsatisfied_reservations": unsatisfied,
                    "reallocation_priority": priority(util_target),
                })
    fact_snap = pd.DataFrame(snap_rows)
    fact_snap.insert(0, "snapshot_id", ["S%07d" % (i + 1) for i in range(len(fact_snap))])

    return {
        "DIM_DATE": dim_date.drop(columns=["dt", "is_exam", "is_weekend_b", "intensity"]),
        "DIM_CATEGORY": dim_cat, "DIM_BRANCH": dim_branch, "DIM_USER": dim_user,
        "DIM_BOOK": dim_book, "FACT_LOAN": fact_loan, "FACT_RESERVATION": fact_res,
        "FACT_INVENTORY_SNAPSHOT": fact_snap,
    }

def main():
    ap = argparse.ArgumentParser(description="Generate the English library-analytics CSVs.")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="output folder (default: ./data)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--keep-french", action="store_true", help="write raw French values (debug)")
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tables = build(a.seed)

    print(f"Writing English CSVs -> {out}")
    for name, df in tables.items():
        if not a.keep_french:
            df = translate_df(name, df.copy())
        df.to_csv(out / f"{name}.csv", index=False, encoding="utf-8")
        print(f"  {name:28s} {df.shape[0]:>7} rows x {df.shape[1]} cols")

    inv = tables["FACT_INVENTORY_SNAPSHOT"]
    last = inv["date_id"].max()
    lm = inv[inv["date_id"] == last]
    crit = (lm["reallocation_priority"] == "Critique").sum()
    unsat = int(lm["unsatisfied_reservations"].sum())
    low = lm[lm["reallocation_priority"] == "Faible"]
    movable = int((low[low["available_copies"] >= 2]["available_copies"] - 1).clip(lower=0).sum())
    print("\nSanity checks (seed 42 should give):")
    print(f"  FACT_LOAN rows .................. {len(tables['FACT_LOAN'])}  (expected 16000)")
    print(f"  FACT_RESERVATION rows .......... {len(tables['FACT_RESERVATION'])}  (expected 3600)")
    print(f"  Critical pairs (last month) .... {crit}  (expected 124)")
    print(f"  Unsatisfied demand (last month)  {unsat}  (expected 353)")
    print(f"  Reallocation coverage % ........ {round(100*movable/unsat,2) if unsat else 'NA'}  (expected ~32.29)")
    print("OK.")


if __name__ == "__main__":
    main()
