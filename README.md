# HMC-NNN Datalab — zorgplannen en opnameduur

Minor Data & Health Innovation · HMC-NNN

Onderzoek naar de vraag of gestandaardiseerde verpleegkundige zorgplandata — **NANDA-I**
diagnoses en **NOC** uitkomstindicatoren — samen met de medische opname-indicatie
(**ICD-10**) iets zeggen over de **opnameduur** (*Length of Stay*) van ziekenhuispatiënten.

## Over de data

`Test datasheet NNN Minor.xlsx` is een **fictieve testexport**: de patiëntnummers, diagnoses
en ICD-10-codes horen niet bij echte patiënten. Daarom staat deze repository openbaar.

Zodra er met een **echte** HMC-export gewerkt wordt, hoort die hier niet in. Zet de
repository dan op privé of — beter — houd het databestand erbuiten via `.gitignore`, en let
erop dat notebook-output ook patiëntgegevens bevat zodra je hem op echte data draait.

## Snel starten

```bash
pip install -r requirements.txt
jupyter lab
```

Open daarna `notebooks/01_base_eda_hmc_nnn.ipynb` en kies *Run All*. De notebooks werken
zowel vanuit de project-root als vanuit de map `notebooks/` — paden worden automatisch
opgezocht, dus je hoeft niets aan te passen.

## De notebooks

| Notebook | Wat het doet |
|---|---|
| [`01_base_eda_hmc_nnn.ipynb`](notebooks/01_base_eda_hmc_nnn.ipynb) | Basis-EDA in vijf pijlers: datakwaliteit, opnameduur vs. diagnoseduur, zorgplan-complexiteit, startmoment van diagnoses, en ICD-10 vs. NANDA/NOC |
| [`02_feature_engineering.ipynb`](notebooks/02_feature_engineering.ipynb) | Bouwt de modelleertabel met uitsluitend dag-0 kenmerken, inclusief leakage-controle en patiënt-gebonden train/test-split |
| [`03_modellering.ipynb`](notebooks/03_modellering.ipynb) | Zet de evaluatieopzet neer: mediaan-baseline, drie featuresets en patiënt-gebonden cross-validatie |

Beide notebooks zijn opgeslagen **mét uitgevoerde output**, zodat je de resultaten ziet
zonder zelf te hoeven draaien.

## Herbruikbare code

Alle inlees- en rekenlogica staat in `src/`. Maak je een nieuw notebook, importeer dan deze
functies in plaats van code te kopiëren — zo rekent iedereen in de groep met dezelfde
definities.

**`src/data_loader.py`**

| Functie | Doet |
|---|---|
| `load_and_clean_hmc_data()` | Leest de Excel, normaliseert kolomnamen, valideert het schema en zet datums/scores om |
| `build_diagnosis_table(df)` | Eén rij per (`Opnamenummer`, `Diagnose`): diagnoseduur, compleetheid, startmoment |
| `build_admission_table(df)` | Eén rij per opname: opnameduur, aantal diagnoses en indicatoren, scorekenmerken |

**`src/features.py`**

| Functie | Doet |
|---|---|
| `build_dag0_features(df)` | Modelleerkenmerken uit **alleen** de metingen van de eerste opnamedag |
| `build_dag0_diagnose_dummies(df)` | 0/1-kolommen per NANDA-diagnose die op dag 0 liep |
| `controleer_geen_leakage(tabel)` | Faalt zodra een kolom van Eindscore, gezondheidswinst of opnamebrede totalen is afgeleid |
| `split_op_patient(tabel)` | Train/test-splitsing waarbij alle opnames van één patiënt aan dezelfde kant blijven |

**`src/modellering.py`**

| Functie | Doet |
|---|---|
| `bouw_featureset(tabel, naam)` | Selecteert de kolommen voor `icd10`, `nanda_noc` of `beide` |
| `maak_pipeline(model, num, cat)` | Imputatie en one-hot-encoding vóór het model, zodat voorbewerking binnen elke fold gebeurt |
| `evalueer_model(tabel, featureset, model)` | Leave-one-patient-out cross-validatie met MAE, RMSE en R² over de out-of-fold voorspellingen |
| `vergelijk_modellen(tabel, modellen)` | Alle combinaties van model en featureset in één overzichtstabel |

## Twee afspraken die je niet moet overslaan

**1. Opnameduur is een ondergrens.** De export bevat geen administratieve opname- en
ontslagdatum. We rekenen `Opnameduur_dagen = max(Meetdatum) − min(Meetdatum)` binnen een
`Opnamenummer`. De echte opname begint dus mogelijk eerder en eindigt later.

**2. Gebruik geen kolommen die het antwoord al bevatten.** Zorgplannen groeien tijdens de
opname: een deel van de diagnoses krijgt pas na dag 0 een Baseline. Kolommen als
`n_diagnoses_totaal`, `gem_gezondheidswinst` en `Is_dagopname` mogen daarom niet als feature
mee in een model dat bij opname voorspelt. Draai `controleer_geen_leakage()` op elke tabel
die je aan een model voert — notebook 02 legt uit waarom.

## Projectstructuur

```
.
├── notebooks/        Analysenotebooks, in volgorde genummerd
├── src/              Herbruikbare modules (inlezen, aggregeren, features)
├── data/processed/   Afgeleide tabellen (gegenereerd door notebook 02)
├── openspec/         Specificaties en het archief van afgeronde changes
├── requirements.txt  Vastgelegde pakketversies
└── Test datasheet NNN Minor.xlsx
```

## Werkwijze: OpenSpec

Dit project gebruikt [OpenSpec](https://github.com/Fission-AI/OpenSpec) om werk vast te
leggen. Afgeronde specificaties staan in `openspec/specs/`, afgeronde changes in
`openspec/changes/archive/`.

```bash
openspec list            # lopende changes
openspec list --specs    # vastgelegde capabilities
openspec validate --specs
```

Nieuw werk begint met een change (`openspec new change <naam>`) met daarin een voorstel,
ontwerp, takenlijst en spec-delta. Pas als alle taken afgevinkt zijn, worden de specs
gepromoveerd en wordt de change gearchiveerd.

## Stand van zaken

De pijplijn loopt van ruwe Excel tot out-of-fold voorspelling en is reproduceerbaar. Op de
huidige **testset van 10 opnames** verslaat geen enkel model de mediaan-baseline, en de
onderzoeksvraag is daarmee nog niet beantwoord — er is simpelweg te weinig data om een effect
te kunnen zien. Dat is het verwachte resultaat bij 10 rijen en 22 kolommen.

De volgende stap is dezelfde code draaien op de volledige HMC-export (~25.000 opnames).
Onderaan notebook 03 staat een checklist van wat je daarbij aanpast: `GroupKFold` in plaats
van leave-one-out, een `min_voorkomens`-drempel voor de diagnose-dummies, en geneste
cross-validatie zodra je gaat tunen.

Vraag daarnaast om de **echte opname- en ontslagdatum**. Zolang `Opnameduur_dagen` het
verschil is tussen de eerste en de laatste meting, voorspel je deels het meetgedrag van de
afdeling in plaats van de opnameduur van de patiënt.
