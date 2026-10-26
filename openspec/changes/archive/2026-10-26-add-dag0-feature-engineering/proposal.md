## Why

De basis-EDA (`setup-reproducible-base-eda`) liet zien dat zorgplannen **tijdens** de opname
groeien: een deel van de NANDA-diagnoses krijgt pas na dag 0 een Baseline-meting. Wie de
opnameduur wil voorspellen op het moment van opname, mag die later toegevoegde informatie niet
gebruiken — anders lekt toekomstinformatie het model in (*data leakage*) en lijkt het model
beter dan het is.

De aggregaties in `build_admission_table()` zijn hiervoor niet veilig: kolommen als
`n_diagnoses_actief_baseline`, `baseline_score_gemiddeld` en `aantal_indicatoren_score_onder_5`
worden berekend over **alle** Baseline-metingen van een opname, inclusief Baselines van
diagnoses die pas op dag 3 startten. Er is dus een aparte, expliciet op dag 0 afgebakende
featurelaag nodig voordat de groep aan modellering begint.

## What Changes

- Toevoegen van een herbruikbare featuremodule `src/features.py` die uit de meting-niveau
  data een **strikt dag-0 featuretabel** bouwt (`build_dag0_features`): alleen metingen met
  `Meet_dag_van_opname == 0` en `Meetmoment == 'Baseline'` tellen mee.
- Toevoegen van NANDA-diagnose dummy-kolommen voor de diagnoses die op dag 0 al liepen
  (`build_dag0_diagnose_dummies`), zodat de inhoud van het zorgplan — niet alleen de omvang —
  als feature beschikbaar is.
- Toevoegen van een expliciete leakage-controle (`controleer_geen_leakage`) die faalt zodra een
  featuretabel een kolom bevat die van `Eindscore`, `Gezondheidswinst` of de totale opname is
  afgeleid.
- Toevoegen van een **patiënt-gebonden** train/test-split (`split_op_patient`) zodat dezelfde
  patiënt nooit in train én test terechtkomt.
- Creëren van `notebooks/02_feature_engineering.ipynb` dat deze stappen uitlegt, de featuretabel
  opbouwt, de dag-0 kolommen naast hun niet-veilige tegenhangers legt en de modelleertabel
  wegschrijft naar `data/processed/`.

## Capabilities

### New Capabilities
- `dag0-feature-engineering`: Afleiden van modelleerfeatures die uitsluitend gebruikmaken van
  informatie die op de eerste opnamedag beschikbaar was, inclusief leakage-controle en een
  patiënt-gebonden datasplitsing.

### Modified Capabilities
<!-- Geen bestaande capabilities worden gewijzigd; careplan-los-eda blijft ongemoeid. -->

## Impact

- **Nieuwe bestanden**:
  - `src/features.py` — herbruikbare featurefuncties voor alle vervolgnotebooks.
  - `notebooks/02_feature_engineering.ipynb` — het gedocumenteerde featurenotebook.
  - `data/processed/modelleertabel_dag0.csv` — de weggeschreven featuretabel.
- **Ongewijzigd**: `src/data_loader.py` en `notebooks/01_base_eda_hmc_nnn.ipynb` blijven zoals ze
  zijn; de featurelaag bouwt erop voort en vervangt niets.
- **Data-afhankelijkheden**: leest dezelfde bron (`Test datasheet NNN Minor.xlsx`) via
  `load_and_clean_hmc_data()` en schrijft alleen naar `data/processed/`.
