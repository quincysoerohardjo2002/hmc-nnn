## 1. Herbruikbare featuremodule (`src/features.py`)

- [x] 1.1 Maak `src/features.py` met `build_dag0_features(df, df_opnames)` die uitsluitend metingen met `Meet_dag_van_opname == 0` en `Meetmoment == 'Baseline'` gebruikt en per `Opnamenummer` de kolommen `n_diagnoses_dag0`, `n_indicatoren_dag0`, `n_diagnoses_actief_dag0`, `n_indicatoren_onder_5_dag0`, `baseline_score_gem_dag0`, `baseline_score_min_dag0`, `pct_score_5_dag0`, `icd10_hoofdcode` en `heeft_dag0_meting` oplevert.
- [x] 1.2 Voeg `build_dag0_diagnose_dummies(df, min_voorkomens=1)` toe die per opname 0/1-kolommen maakt voor de NANDA-diagnoses die op dag 0 liepen, met samenvoeging van zeldzame diagnoses in `diag_overig`.
- [x] 1.3 Voeg `controleer_geen_leakage(tabel)` toe die een `ValueError` geeft zodra een kolomnaam van `Eindscore`, `Gezondheidswinst`, diagnoseduur of opnamebrede totalen is afgeleid, met een expliciete witte lijst voor `Opnameduur_dagen`, `Opnamenummer` en `Patientnr`.
- [x] 1.4 Voeg `split_op_patient(tabel, test_fractie, seed)` toe die unieke `Patientnr`-waarden verdeelt zodat alle opnames van dezelfde patiënt aan dezelfde kant van de splitsing staan.

## 2. Featurenotebook (`notebooks/02_feature_engineering.ipynb`)

- [x] 2.1 Maak `notebooks/02_feature_engineering.ipynb` met een introductie die aansluit op notebook 01 en uitlegt wat data leakage in dit project concreet betekent.
- [x] 2.2 Bouw de dag-0 featuretabel met `build_dag0_features` en toon per kolom de herkomst en de verdeling.
- [x] 2.3 Zet de dag-0 kolommen naast hun opnamebrede tegenhangers uit `df_opnames` en visualiseer het verschil, zodat zichtbaar is welke informatie bij opname nog niet bestond.
- [x] 2.4 Voeg de NANDA-dummy-kolommen toe en laat zien welke diagnoses op dag 0 het vaakst voorkomen.
- [x] 2.5 Draai `controleer_geen_leakage` op de definitieve modelleertabel en demonstreer dat de controle ook daadwerkelijk faalt op een bewust vervuilde tabel.
- [x] 2.6 Maak de patiënt-gebonden train/test-split met `split_op_patient` en controleer dat er geen patiënt in beide delen zit.
- [x] 2.7 Schrijf de modelleertabel weg naar `data/processed/modelleertabel_dag0.csv` en sluit af met een overdracht naar de modelleerstap.

## 3. Verificatie & Uitvoerbaarheid

- [x] 3.1 Voer alle cellen van `notebooks/02_feature_engineering.ipynb` van boven naar beneden uit en sla de outputs op, zodat klasgenoten de resultaten direct zien bij het openen.
