## 1. Evaluatiemodule (`src/modellering.py`)

- [x] 1.1 Maak `src/modellering.py` met `bouw_featureset(tabel, naam)` die voor `icd10`, `nanda_noc` en `beide` de bijbehorende kolommen selecteert en sleutels, labels en de doelvariabele altijd uitsluit.
- [x] 1.2 Voeg `maak_pipeline(model, numerieke_kolommen, categorische_kolommen)` toe die een `ColumnTransformer` met `SimpleImputer` (mediaan) en `OneHotEncoder(handle_unknown="ignore")` voor het model plaatst, zodat preprocessing binnen elke fold gebeurt.
- [x] 1.3 Voeg `evalueer_model(tabel, featureset, model)` toe die met `LeaveOneGroupOut` op `Patientnr` out-of-fold voorspellingen verzamelt en daarover MAE, RMSE en R² berekent.
- [x] 1.4 Voeg `vergelijk_modellen(tabel, modellen, featuresets)` toe die alle combinaties doorrekent en één overzichtstabel teruggeeft, gesorteerd op MAE.

## 2. Modelleernotebook (`notebooks/03_modellering.ipynb`)

- [x] 2.1 Maak `notebooks/03_modellering.ipynb` met een introductie die aansluit op notebook 02 en uitlegt waarom de evaluatieopzet hier belangrijker is dan het model.
- [x] 2.2 Laad `data/processed/modelleertabel_dag0.csv` met een terugval op opnieuw opbouwen vanuit de bron, draai `controleer_geen_leakage` en toon de drie featuresets met hun kolomaantallen.
- [x] 2.3 Zet de mediaan-baseline neer en laat zien wat die in dagen aan MAE oplevert.
- [x] 2.4 Draai de vergelijking van baseline, Ridge en RandomForest over de drie featuresets en toon de resultatentabel.
- [x] 2.5 Visualiseer de MAE per featureset tegen de baseline, en toon voorspeld versus werkelijk per model.
- [x] 2.6 Sluit af met een expliciete conclusie over wat bij N = 10 wel en niet gezegd kan worden, plus een checklist voor het herhalen op de volledige dataset.

## 3. Verificatie & Uitvoerbaarheid

- [x] 3.1 Voeg `scikit-learn` toe aan `requirements.txt`.
- [x] 3.2 Voer alle cellen van `notebooks/03_modellering.ipynb` van boven naar beneden uit en sla de outputs op, zodat klasgenoten de resultaten direct zien bij het openen.
