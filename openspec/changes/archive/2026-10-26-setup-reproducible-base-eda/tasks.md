## 1. Omgeving & Reproduceerbare Data Ingestion

- [x] 1.1 Maak `requirements.txt` aan met gepinde, stabiele versies van `pandas`, `openpyxl`, `numpy`, `matplotlib`, `seaborn`, `scipy` en `jupyter` zodat alle groepsleden dezelfde omgeving hebben.
- [x] 1.2 Maak een herbruikbare data-loader module `src/data_loader.py` met pad-resolutie (`resolve_data_path`), kolomnormalisatie (`'RAPm vNandaNicNoc_Probleem'[Opnamenummer]` $\rightarrow$ `Opnamenummer`, `Score oms` $\rightarrow$ `Score_omschrijving`), schema-validatie en datum/tijd/score type-conversie (`load_and_clean_hmc_data`).
- [x] 1.3 Voeg aggregatiefuncties toe aan `src/data_loader.py` (`build_diagnosis_table` en `build_admission_table`) die op basis van `Opnamenummer` de totale opnameduur (`max(Meetdatum) - min(Meetdatum)`), individuele diagnoseduur (`Eindscore` min `Baseline`), compleetheidsstatus en zorgplan-complexiteitsmetrics (`n_diagnoses_totaal`, `n_diagnoses_dag0`, `n_diagnoses_actief_baseline`, `n_indicatoren`) berekenen.

## 2. Basis EDA Notebook Opbouwen (`notebooks/01_base_eda_hmc_nnn.ipynb`)

- [x] 2.1 Maak `notebooks/01_base_eda_hmc_nnn.ipynb` aan met een duidelijke introductie voor klasgenoten (projectdoel HMC-NNN, instructie voor gebruik en de data-import & validatiestap).
- [x] 2.2 Implementeer **Pijler 1 (Datakwaliteit & Zorgplan-integriteit)** in het notebook: overzicht van ontbrekende waarden, verdeling van `MeetScore` (inclusief het aandeel score `5`), en analyse + visualisatie van complete diagnoses versus wees-metingen (enkel `Baseline` of enkel `Eindscore`).
- [x] 2.3 Implementeer **Pijler 2 (Opnameduur vs. Individuele Diagnoseduur)** in het notebook: berekening en visualisatie van de totale `Opnameduur_dagen` per opname (inclusief dagopnames van 0 dagen), de doorlooptijd per NANDA-diagnose en een visuele Gantt-achtige zorgplan-tijdlijn per opname.
- [x] 2.4 Implementeer **Pijler 3 (Zorgplan-complexiteit vs. Opnameduur)** in het notebook: toets en visualiseer de relatie (Spearman/Pearson correlatie + scatter/boxplots) tussen het aantal diagnoses/indicatoren in een zorgplan (`n_diagnoses_totaal`, `n_diagnoses_dag0`, `n_diagnoses_actief_baseline`) en de totale opnameduur.
- [x] 2.5 Implementeer **Pijler 4 (Tijdstip van Diagnose-start & Data Leakage)** en **Pijler 5 (ICD-10 vs. NANDA/NOC interactie)** in het notebook: analyse van `start_dag_offset` (Dag 0 vs. latere diagnoses) en vergelijking van opnameduur en zorgplannen binnen dezelfde ICD-10 hoofddiagnose (zoals `S72.00`), afgesloten met concrete aanbevelingen voor Feature Engineering & Modelleren.

## 3. Verificatie & Uitvoerbaarheid

- [x] 3.1 Voer alle cellen van `notebooks/01_base_eda_hmc_nnn.ipynb` van boven naar beneden uit (en sla de gegenereerde tabellen en grafieken op in de notebook-outputs) zodat klasgenoten direct de resultaten zien bij het openen.
