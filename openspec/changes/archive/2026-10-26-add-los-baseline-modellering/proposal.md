## Why

Na de basis-EDA (`setup-reproducible-base-eda`) en de leakage-vrije featurelaag
(`add-dag0-feature-engineering`) ligt er een modelleertabel klaar, maar nog geen manier om
modellen te trainen en eerlijk met elkaar te vergelijken. Zonder vaste evaluatieopzet gaat elk
groepslid straks met een eigen splitsing en eigen metriek werken, en zijn de resultaten
onderling niet te vergelijken.

Bovendien is de onderzoeksvraag — *voegt het verpleegkundige zorgplan iets toe bovenop de
medische ICD-10-diagnose?* — pas te beantwoorden als je drie modellen op **precies dezelfde
manier** evalueert: alleen ICD-10, alleen NANDA/NOC, en beide samen.

## What Changes

- Toevoegen van `src/modellering.py` met een vaste evaluatieopzet:
  - drie benoemde featuresets (`icd10`, `nanda_noc`, `beide`) die uit de modelleertabel worden
    afgeleid, zodat iedereen dezelfde kolommen gebruikt;
  - een `sklearn`-pipeline die categorische kolommen one-hot encodeert en ontbrekende numerieke
    waarden imputeert, zodat de preprocessing binnen elke fold gebeurt en niet eroverheen;
  - **Leave-One-Group-Out cross-validatie op `Patientnr`**, zodat dezelfde patiënt nooit in train
    en test tegelijk zit;
  - een vergelijkingstabel met MAE, RMSE en R² over de verzamelde out-of-fold voorspellingen.
- Creëren van `notebooks/03_modellering.ipynb` dat de drie featuresets tegen een
  mediaan-baseline afzet, de resultaten visualiseert en expliciet concludeert wat je bij
  N = 10 wel en niet mag zeggen.

## Capabilities

### New Capabilities
- `los-baseline-modellering`: Trainen en eerlijk vergelijken van opnameduur-voorspellers op basis
  van dag-0 kenmerken, met patiënt-gebonden cross-validatie en een verplichte baseline.

### Modified Capabilities
<!-- Geen bestaande capabilities worden gewijzigd. -->

## Impact

- **Nieuwe bestanden**:
  - `src/modellering.py` — featuresets, pipeline en evaluatie.
  - `notebooks/03_modellering.ipynb` — het modelleernotebook.
- **Gewijzigd**: `requirements.txt` krijgt `scikit-learn`.
- **Ongewijzigd**: `src/data_loader.py`, `src/features.py` en de notebooks 01 en 02 blijven zoals
  ze zijn; dit bouwt er alleen op voort.
- **Data-afhankelijkheden**: leest `data/processed/modelleertabel_dag0.csv`, met een terugval op
  het opnieuw opbouwen vanuit de bron als dat bestand er nog niet is.
