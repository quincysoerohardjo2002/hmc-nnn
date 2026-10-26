## Context

Binnen het HMC-NNN Datalab project onderzoeken we met een groep studenten hoe verpleegkundige zorgplandata (NANDA-I diagnoses en NOC-uitkomstindicatoren) en medische opname-indicaties (ICD-10) samenhangen met de opnameduur van patiënten. De huidige dataset (`Test datasheet NNN Minor.xlsx`) is een test-export op **meting-niveau** (meerdere rijen per patiënt/opname), waarbij elke rij één NOC-indicator op één `Meetmoment` (`Baseline` of `Eindscore`) binnen één NANDA-`Diagnose` en één `Opnamenummer` voorstelt.

Omdat meerdere klasgenoten tegelijkertijd aan analyses en latere modellen gaan werken, moet er een gestandaardiseerd en volledig reproduceerbaar startpunt zijn.

## Goals / Non-Goals

**Goals:**
- Een reproduceerbare data-import en opschoon-pijplijn waarmee iedere student op Windows/macOS/Linux zonder pad-aanpassingen het Excel-bestand kan inladen.
- Duidelijke transformatie van **meting-niveau** (226 rijen in de testset) naar twee geaggregeerde analysetabellen:
  1. **Diagnose-niveau (`df_diagnoses`)**: 1 rij per (`Opnamenummer`, `Diagnose`) met startdatum (`Baseline`), einddatum (`Eindscore`), individuele diagnoseduur en compleetheidsstatus.
  2. **Opname-/Zorgplan-niveau (`df_opnames`)**: 1 rij per `Opnamenummer` met de totale opnameduur (`max(Meetdatum) - min(Meetdatum)`), ICD-10 hoofddiagnose, aantal unieke NANDA-diagnoses, aantal unieke NOC-indicatoren, aantal op Dag 0 gestarte diagnoses en gemiddelde/laagste baseline-score.
- Een overzichtelijk, goed gedocumenteerd Jupyter Notebook (`notebooks/01_base_eda_hmc_nnn.ipynb`) waarin alle 5 pijlers van de basis-EDA visueel en statistisch worden uitgewerkt.

**Non-Goals:**
- Het nu al trainen of tunen van Machine Learning predictiemodellen (dit volgt na de EDA).
- Het wijzigen of overschrijven van het originele bronbestand `Test datasheet NNN Minor.xlsx`.

## Decisions

### 1. Projectstructuur: Herbruikbare data-loader + Centraal EDA Notebook
- **Keuze**: We plaatsen een schone, herbruikbare data-loader module in `src/data_loader.py` (of direct aanpasbaar én aanroepbaar vanuit het notebook met een fallback zodat het notebook ook standalone werkt) en het EDA-notebook in `notebooks/01_base_eda_hmc_nnn.ipynb`, ondersteund door een `requirements.txt` in de root.
- **Waarom**: Klasgenoten die later een nieuw notebook maken (bijv. voor feature engineering of modellering) kunnen direct dezelfde `load_and_clean_hmc_data()` en `build_diagnosis_table()` / `build_admission_table()` functies importeren zonder code te kopiëren, terwijl alles in het basis-notebook ook transparant wordt uitgelegd.
- **Alternatieven overwogen**: Alleen losse codecellen in één notebook zonder herbruikbare functies — dit leidt in studentengroepen snel tot verschillende definities van opnameduur in verschillende notebooks.

### 2. Definitie van Opnameduur (LOS) en Diagnoseduur
- **Keuze**:
  - **Opname-niveau (`Opnameduur_dagen`)**: Voor elk uniek `Opnamenummer` is `opname_start = min(Meetdatum)` over alle metingen binnen die opname, en `opname_eind = max(Meetdatum)` over alle metingen binnen die opname. `Opnameduur_dagen = (opname_eind - opname_start).dt.days`.
  - **Diagnose-niveau (`Diagnoseduur_dagen`)**: Voor elke unieke (`Opnamenummer`, `Diagnose`) combinatie is `diagnose_start = min(Meetdatum waar Meetmoment == 'Baseline')` en `diagnose_eind = max(Meetdatum waar Meetmoment == 'Eindscore')`.
- **Waarom**: Er is in de export geen aparte administratieve opname- of ontslagdatum-kolom aanwezig. Een zorgplan (`Opnamenummer`) omvat meerdere diagnoses die op verschillende dagen kunnen starten en eindigen; de vroegste en laatste datum binnen hetzelfde `Opnamenummer` vormen daardoor de beste begrenzing van de totale ziekenhuisopname.

### 3. Scheiding tussen 'Alle Diagnoses' en 'Dag-0 / Actieve Diagnoses' in Complexiteitsanalyse
- **Keuze**: In `df_opnames` berekenen we zowel:
  - `n_diagnoses_totaal`: totaal aantal unieke NANDA-diagnoses gedurende de hele opname.
  - `n_diagnoses_dag0`: aantal unieke NANDA-diagnoses waarvan de `Baseline` op de eerste dag van de opname (`start_dag_offset == 0`) is geregistreerd.
  - `n_diagnoses_actief_baseline`: aantal unieke NANDA-diagnoses waarbij ten minste één indicator op `Baseline` een `MeetScore < 5` heeft (omdat score `5` in NOC vaak staat voor "Geen probleem / Niet beperkt").
- **Waarom**:
  1. Als een patiënt langer ligt, krijgt deze mogelijk gedurende de opname extra diagnoses erbij (omgekeerde causaliteit / *data leakage* voor een predictiemodel bij opname). Door `n_diagnoses_totaal` én `n_diagnoses_dag0` te vergelijken, toetsen we de hypothese zuiver.
  2. Circa 68% van de metingen in de testset heeft score `5`. Onderscheid maken tussen geregistreerde diagnoses met score `5` en diagnoses met daadwerkelijke beperkingen (`< 5`) geeft veel scherper inzicht in de echte zorgzwaarte.

## Risks / Trade-offs

- **[Risk] Kleine steekproefomvang in de test-dataset ($N = 10$ opnames, 226 rijen)** → **Mitigatie**: Alle aggregaties, tabellen, correlaties (Spearman/Pearson) en grafieken worden zo geprogrammeerd dat ze zowel op $N = 10$ werken als straks één-op-één schalen naar de volledige HMC-dataset (~25.000 opnames). In het notebook zetten we bij statistische toetsen expliciet een toelichting over de steekproefgrootte van de testset.
- **[Risk] Wees-metingen (diagnoses zonder Baseline of zonder Eindscore) en herhaalde Eindscores** → **Mitigatie**: Voor totale opnameduur gebruiken we `min(Meetdatum)` en `max(Meetdatum)` ongeacht het label `Meetmoment`, zodat een ontbrekend `Eindscore`-label de totale opnameduur niet breekt. Voor individuele diagnoseduur rapporteren we wees-metingen apart in Pijler 1 (Datakwaliteit).
- **[Risk] Verschillende werkdirectory's bij klasgenoten (VS Code vs. Jupyter Lab)** → **Mitigatie**: De pad-resolver zoekt automatisch naar `Test datasheet NNN Minor.xlsx` in `./` en `../`, zodat het notebook altijd werkt ongeacht vanuit welke map Jupyter wordt gestart.
