# LOS Baseline Modellering

## Purpose

Trainen en eerlijk vergelijken van opnameduur-voorspellers op basis van dag-0
kenmerken: drie benoemde featuresets, voorbewerking binnen de cross-validatiefold,
patient-gebonden Leave-One-Group-Out evaluatie en een verplichte mediaan-baseline.

Implementatie: `src/modellering.py` (`bouw_featureset`, `maak_pipeline`,
`evalueer_model`, `vergelijk_modellen`) en `notebooks/03_modellering.ipynb`.

## Requirements

### Requirement: Named Feature Sets for the Research Question
Het systeem SHALL drie benoemde featuresets leveren — `icd10` (alleen de medische hoofdcode),
`nanda_noc` (alleen de dag-0 zorgplankenmerken en diagnose-dummies) en `beide` (de vereniging) —
waarbij sleutelkolommen, labelkolommen en de doelvariabele altijd buiten de features blijven.

#### Scenario: Sleutels en doelvariabele komen nooit in de features
- **WHEN** een featureset wordt opgebouwd uit de modelleertabel
- **THEN** bevatten de geselecteerde kolommen geen `Opnamenummer`, `Patientnr`, `ICD10Code`,
  `ICD10Omschrijving` of `Opnameduur_dagen`

#### Scenario: De drie sets zijn onderling vergelijkbaar
- **WHEN** dezelfde modelleertabel met `icd10`, `nanda_noc` en `beide` wordt doorgerekend
- **THEN** is `beide` exact de vereniging van de kolommen van `icd10` en `nanda_noc`, zodat het
  verschil in prestatie toe te schrijven is aan de toegevoegde kolommen en niet aan een andere opzet

### Requirement: Preprocessing Inside the Cross-Validation Fold
Het systeem SHALL imputatie van ontbrekende numerieke waarden en one-hot-encoding van categorische
kolommen uitvoeren binnen een pipeline die per fold opnieuw wordt gefit, en niet eenmalig over de
volledige dataset.

#### Scenario: Ongeziene categorie in een testfold
- **WHEN** een opname in de testfold een `icd10_hoofdcode` heeft die in de trainfold niet voorkomt
- **THEN** draait de evaluatie door zonder fout en krijgt die rij enkel nullen voor het
  one-hot-blok

### Requirement: Patient-Grouped Out-of-Fold Evaluation
Het systeem SHALL de modelprestatie bepalen met Leave-One-Group-Out cross-validatie gegroepeerd op
`Patientnr`, waarbij de out-of-fold voorspellingen eerst worden verzameld en de metrieken (MAE,
RMSE, R²) daarna één keer over de volledige vector worden berekend.

#### Scenario: Geen patient in train en test tegelijk
- **WHEN** een patiënt meerdere opnames in de modelleertabel heeft
- **THEN** zitten al die opnames in dezelfde fold en wordt er voor die opnames nooit voorspeld met
  een model dat op diezelfde patiënt getraind is

#### Scenario: Elke opname krijgt precies een out-of-fold voorspelling
- **WHEN** de evaluatie is afgerond
- **THEN** is het aantal verzamelde voorspellingen gelijk aan het aantal rijen in de modelleertabel

### Requirement: Mandatory Median Baseline
Het systeem SHALL in elke modelvergelijking een baseline opnemen die altijd de mediane opnameduur
voorspelt, zodat zichtbaar is of een model werkelijk iets toevoegt.

#### Scenario: Model presteert slechter dan de baseline
- **WHEN** een getraind model een hogere MAE heeft dan de mediaan-baseline
- **THEN** staat dat in de resultatentabel naast elkaar, zodat de vergelijking niet alleen tussen
  de getrainde modellen onderling plaatsvindt
