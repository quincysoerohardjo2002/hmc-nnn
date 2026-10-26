## Context

Uit de basis-EDA bleek dat zorgplannen groeien tijdens de opname: in de testset start een deel
van de NANDA-diagnoses pas na dag 0. De bestaande aggregatielaag (`build_admission_table`) telt
over de **hele** opname en is daarmee geschikt voor beschrijvende analyse, maar niet als
featurebron voor een model dat bij opname voorspelt.

Deze change voegt daarom een tweede, strikt afgebakende laag toe. De scheiding is bewust:
`data_loader.py` beschrijft wat er gebeurd is, `features.py` beschrijft wat je op dag 0 wist.

## Goals / Non-Goals

**Goals:**
- Eén functie die een modelleertabel oplevert waarvan **elke kolom** herleidbaar is tot een
  meting op de eerste opnamedag.
- Een controle die leakage hard laat falen in plaats van stilzwijgend door te laten.
- Een splitsing op patiëntniveau, zodat de groep bij de stap naar modellering niet per ongeluk
  dezelfde patiënt in train en test krijgt.
- Een notebook dat uitlegt **waarom** een kolom wel of niet mee mag, met de naïeve en de veilige
  variant naast elkaar.

**Non-Goals:**
- Het trainen, tunen of evalueren van modellen (dat is de volgende change).
- Het aanpassen van `src/data_loader.py` of notebook 01.
- Imputatie-strategieën of schaaltransformaties; die horen bij het modelleerrecept, niet bij de
  featuredefinitie.

## Decisions

### 1. Dag 0 is `Meet_dag_van_opname == 0`, niet "de eerste meting per diagnose"
- **Keuze**: een meting telt als dag-0-informatie wanneer haar `Meetdatum` gelijk is aan
  `Opname_startdatum` én het `Meetmoment` `Baseline` is.
- **Waarom**: `Opname_startdatum` is per definitie `min(Meetdatum)` binnen de opname, dus
  `Meet_dag_van_opname == 0` is precies "op de eerste dag waarop iets gemeten is". Een regel per
  diagnose ("neem de eerste meting van elke diagnose") zou juist de later toegevoegde diagnoses
  binnenhalen, wat we hier willen uitsluiten.
- **Alternatieven overwogen**: een tijdsvenster van 24 uur op basis van `Meet_datetime`. Afgevallen
  omdat de meettijden in de export niet betrouwbaar genoeg zijn om een uur-grens op te baseren;
  kalenderdag is grover maar eerlijker.

### 2. Dag-0 varianten krijgen een eigen naam, naast de bestaande kolommen
- **Keuze**: de featuretabel gebruikt `*_dag0`-namen (`n_diagnoses_dag0`, `n_indicatoren_dag0`,
  `baseline_score_min_dag0`, ...) en neemt de opnamebrede kolommen niet over.
- **Waarom**: dezelfde naam voor twee verschillende definities is de snelste route naar een fout
  die niemand opmerkt. Door ze expliciet te scheiden kan het notebook beide naast elkaar tonen en
  kan `controleer_geen_leakage` op naam filteren.

### 3. Leakage-controle op kolomnaam, met een expliciete witte lijst
- **Keuze**: `controleer_geen_leakage(tabel)` faalt met een `ValueError` zodra een kolomnaam een
  verboden fragment bevat (`eind`, `gezondheidswinst`, `duur`, `totaal`, `later`), tenzij de kolom
  in de witte lijst staat (`Opnameduur_dagen` als doelvariabele, `Opnamenummer`, `Patientnr`).
- **Waarom**: een controle op naam is grof maar leesbaar en werkt ook als iemand later zelf een
  kolom toevoegt. De fout is luid: liever een false positive die je wegwuift met de witte lijst
  dan een leakage die je nooit ziet.
- **Alternatieven overwogen**: herkomst bijhouden per kolom (lineage). Te zwaar voor een
  studentenproject van deze omvang.

### 4. Splitsen op `Patientnr`, niet op rij
- **Keuze**: `split_op_patient()` verdeelt unieke patiëntnummers over train en test en wijst
  daarna alle opnames van die patiënt toe aan dezelfde kant.
- **Waarom**: in de volledige HMC-dataset kan dezelfde patiënt meerdere opnames hebben. Een
  rij-gewijze splitsing geeft dan een te optimistisch testresultaat. In de testset heeft elke
  patiënt precies één opname, dus het verschil is daar nog niet zichtbaar — reden te meer om de
  functie nu al goed te zetten.

## Risks / Trade-offs

- **[Risk] Opnames zonder dag-0 Baseline-metingen** → **Mitigatie**: `build_dag0_features`
  reindexeert over alle opnames, vult tellingen met `0` en scores met `NaN`, en geeft een kolom
  `heeft_dag0_meting` mee zodat zulke opnames bewust uitgesloten of apart behandeld kunnen worden.
  In de testset komt dit niet voor, in de volledige export vrijwel zeker wel.
- **[Risk] NANDA-dummies exploderen bij de volledige dataset** → **Mitigatie**:
  `build_dag0_diagnose_dummies` heeft een `min_voorkomens`-drempel; diagnoses die zeldzamer zijn
  vallen samen in `diag_overig`. Op de testset staat die drempel op 1 zodat alles zichtbaar blijft.
- **[Risk] ICD-10 op volledige code is te fijnmazig** → **Mitigatie**: naast `ICD10Code` leveren we
  `icd10_hoofdcode` (de eerste drie tekens, bijv. `S72`) zodat de groep op beide niveaus kan
  modelleren en vergelijken.
