# HMC-NNN Datalab — zorgplannen en opnameduur

Minor Data & Health Innovation · HMC-NNN

Onderzoek naar de vraag of gestandaardiseerde verpleegkundige zorgplandata — **NANDA-I**
diagnoses en **NOC** uitkomstindicatoren — samen met de medische opname-indicatie
(**ICD-10**) iets zeggen over de **opnameduur** (*Length of Stay*) van ziekenhuispatiënten.

> ## ⚠️ Deze repository bevat fictieve patiëntgegevens
>
> `Test datasheet NNN Minor.xlsx`, de uitgevoerde notebooks en `data/processed/` bevatten
> patiëntnummers, verpleegkundige diagnoses en ICD-10-codes. **Houd deze repository privé**
> en deel toegang alleen met groepsgenoten en docenten. Maak hem niet openbaar en plak geen
> notebook-output in publieke kanalen.

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

## Volgende stap

`notebooks/03_modellering.ipynb` bestaat nog niet. De afspraken daarvoor staan onderaan
notebook 02: begin met een baseline die altijd de mediane opnameduur voorspelt, en vergelijk
drie modellen — alleen ICD-10, alleen NANDA/NOC dag-0, en beide samen. Het verschil tussen
het eerste en het laatste is het antwoord op de onderzoeksvraag.
