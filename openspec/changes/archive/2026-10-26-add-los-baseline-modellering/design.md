## Context

De modelleertabel uit notebook 02 heeft 10 rijen (10 opnames, 10 patiënten) en ~27 kolommen.
Dat is omgekeerd aan wat je voor modellering wilt: meer kolommen dan rijen. Elk model dat we hier
trainen gaat overfitten, en elke uitkomst is ruis.

Dat is geen reden om deze stap over te slaan, maar wel een reden om hem anders in te richten: het
doel van deze change is een **evaluatieopzet die correct is en meeschaalt**, niet een model dat
nu al iets voorspelt. Op de volledige HMC-dataset (~25.000 opnames) draait exact dezelfde code.

## Goals / Non-Goals

**Goals:**
- Eén plek waar vastligt welke kolommen bij welke featureset horen, zodat drie groepsleden met
  dezelfde `icd10`-set werken.
- Preprocessing binnen de cross-validatie, niet ervoor — anders lekt informatie uit de testfold
  via de imputatie en de one-hot-categorieën.
- Een baseline die niets leert (altijd de mediane opnameduur) als ondergrens bij elke vergelijking.
- Metrieken in dagen (MAE, RMSE), zodat een uitkomst uit te leggen is aan een verpleegkundige.

**Non-Goals:**
- Hyperparameter-tuning. Met 10 rijen is elke tuning curve fitting op ruis.
- Feature selection of dimensiereductie.
- Een "beste model" aanwijzen. Deze change levert de meetlat, niet de winnaar.

## Decisions

### 1. Leave-One-Group-Out op `Patientnr` in plaats van één train/test-split
- **Keuze**: `LeaveOneGroupOut` met `groups = Patientnr`; de voorspellingen van alle folds worden
  verzameld en pas daarna doorgerekend naar MAE, RMSE en R².
- **Waarom**: bij 10 rijen levert één split van 70/30 een testset van 3 opnames op — de uitkomst
  hangt dan volledig af van welke 3 dat zijn. Met LOGO krijgt elke opname precies één
  out-of-fold voorspelling en gebruik je alle data. Groeperen op patiënt houdt bovendien stand
  wanneer dezelfde patiënt straks meerdere opnames heeft.
- **Alternatieven overwogen**: `GroupKFold` met 5 folds. Prima op de volledige dataset en met één
  regel te wisselen; bij 10 groepen valt dat samen met LOGO zonder iets toe te voegen.

### 2. Metrieken over verzamelde out-of-fold voorspellingen, niet gemiddeld per fold
- **Keuze**: `cross_val_predict` verzamelt eerst alle voorspellingen; de metriek wordt één keer
  over die volledige vector berekend.
- **Waarom**: bij LOGO bevat elke fold één observatie. Een R² per fold bestaat dan niet en een MAE
  per fold middelen geeft bij ongelijke foldgroottes een vertekend getal.

### 3. Drie featuresets, één naam per set
- **Keuze**: `icd10` (alleen `icd10_hoofdcode`), `nanda_noc` (de `*_dag0`-kolommen plus de
  `diag_*`-dummies) en `beide` (de vereniging). Sleutels (`Opnamenummer`, `Patientnr`), labels
  (`ICD10Code`, `ICD10Omschrijving`) en de doelvariabele vallen er altijd buiten.
- **Waarom**: het verschil tussen `icd10` en `beide` is precies de onderzoeksvraag. Door die drie
  sets in code vast te leggen kan niemand er per ongeluk een andere kolomselectie van maken.

### 4. Mediaan-baseline als verplichte ondergrens
- **Keuze**: `DummyRegressor(strategy="median")` draait als eerste model in elke vergelijking.
- **Waarom**: opnameduur is rechtsscheef; de mediaan is de voorspelling die de MAE minimaliseert
  als je niets weet. Een model dat daar niet overheen komt, voegt niets toe — hoe fraai de code
  ook is. Dat moet zichtbaar in de tabel staan, niet in een voetnoot.

### 5. Ridge en RandomForest als illustratie, niet als kandidaat-winnaar
- **Keuze**: naast de baseline draaien `Ridge` (lineair, geregulariseerd) en een kleine
  `RandomForestRegressor`.
- **Waarom**: Ridge is bij meer kolommen dan rijen de enige lineaire variant die niet ontspoort.
  RandomForest staat erbij om te laten zien dat een krachtiger model bij deze N juist *slechter*
  scoort dan de mediaan — dat is de les, niet een tegenvaller.

## Risks / Trade-offs

- **[Risk] De resultaten worden gelezen als een antwoord op de onderzoeksvraag** → **Mitigatie**:
  het notebook zet boven én onder de resultatentabel expliciet dat N = 10 is, dat de verschillen
  binnen de ruis vallen en dat pas bij de volledige dataset conclusies getrokken worden.
- **[Risk] Ongeziene ICD-10-categorie in een testfold** → **Mitigatie**:
  `OneHotEncoder(handle_unknown="ignore")`, zodat een patiënt met een unieke code geen crash geeft
  maar een rij met enkel nullen voor dat blok.
- **[Risk] Scorekolommen zijn `NaN` bij opnames zonder dag-0 meting** → **Mitigatie**: een
  `SimpleImputer` op de mediaan binnen de pipeline, dus per fold berekend.
