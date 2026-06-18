# Mesures DAX

A reecrire sur le modele 3 facts. Plus de filtre event_type :
- emprunts -> FACT_LOAN
- reservations -> FACT_RESERVATION
- stock / reallocation -> FACT_INVENTORY_SNAPSHOT (agreger un snapshot avec AVERAGE/LASTNONBLANK, jamais SUM sur l axe temps).
