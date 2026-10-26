## ADDED Requirements

### Requirement: Care Plan and Admission Length of Stay (LOS) Calculation
Het systeem SHALL per unieke opname (`Opnamenummer`) de startdatum van de opname bepalen als de vroegste `Meetdatum` (`min(Meetdatum)`) en de einddatum als de laatste `Meetdatum` (`max(Meetdatum)`), en hieruit de totale opnameduur in dagen (`Opnameduur_dagen`) berekenen.

#### Scenario: Berekening van totale opnameduur over meerdere diagnoses heen
- **WHEN** een opname meerdere NANDA-diagnoses heeft die op verschillende dagen starten en eindigen (zoals `Opnamenummer == 1` met vroegste meting op dag X en laatste meting 7 dagen later)
- **THEN** wordt `Opnameduur_dagen` voor die opname berekend als `7` dagen (`max(Meetdatum) - min(Meetdatum)`)

#### Scenario: Dagopname op dezelfde datum
- **WHEN** alle metingen binnen een `Opnamenummer` op exact dezelfde kalenderdag plaatsvinden (zoals `Opnamenummer == 10`)
- **THEN** wordt `Opnameduur_dagen` berekend als `0` dagen en herkend als dagopname

### Requirement: Individual Nursing Diagnosis Duration and Completeness Analysis
Het systeem SHALL per combinatie van (`Opnamenummer`, `Diagnose`) de individuele diagnoseduur berekenen (`max(Eindscore datum) - min(Baseline datum)`) en vastleggen of een diagnose compleet is (zowel `Baseline` als `Eindscore` aanwezig) of een wees-meting betreft (enkel `Baseline` of enkel `Eindscore`).

#### Scenario: Diagnose met zowel Baseline als Eindscore
- **WHEN** een NANDA-diagnose binnen een zorgplan ten minste één `Baseline` en één `Eindscore` meting heeft
- **THEN** wordt de diagnose geclassificeerd als `Compleet` en wordt de individuele diagnoseduur in dagen berekend

#### Scenario: Diagnose mist Baseline of Eindscore
- **WHEN** een NANDA-diagnose enkel een `Baseline` (bijv. *Angst* bij Patiënt 7) of enkel een `Eindscore` (bijv. *Risico op vallen* bij Patiënt 9) heeft
- **THEN** wordt de diagnose gemarkeerd als respectievelijk `Enkel Baseline` of `Enkel Eindscore` in het datakwaliteitsoverzicht

### Requirement: Care Plan Complexity vs. Length of Stay Analysis
Het notebook SHALL per zorgplan (`Opnamenummer`) het aantal unieke NANDA-diagnoses (`aantal_diagnoses`), het aantal unieke NOC-indicatoren (`aantal_indicatoren`), en het aantal diagnoses met daadwerkelijke klachten bij aanvang (`Baseline MeetScore < 5`) berekenen en de relatie met `Opnameduur_dagen` analyseren en visualiseren.

#### Scenario: Vergelijking van aantal diagnoses met opnameduur
- **WHEN** de complexiteitsanalyse in het EDA-notebook wordt uitgevoerd
- **THEN** toont het notebook een overzichtstabel, correlatiemaat (Spearman/Pearson) en visualisatie van `aantal_diagnoses` en `aantal_indicatoren` ten opzichte van `Opnameduur_dagen`

### Requirement: Diagnosis Timing (Day 0 vs. Late Onset) and ICD-10 Context Analysis
Het notebook SHALL per diagnose bepalen hoeveel dagen na de start van de opname de eerste `Baseline`-meting plaatsvindt (`start_dag_offset = Baseline_datum - Opname_startdatum`) en de opnameduur en NANDA-zorgplannen vergelijken binnen en tussen medische `ICD10Code`-groepen.

#### Scenario: Onderscheid tussen opname-diagnoses (Dag 0) en latere diagnoses
- **WHEN** een NANDA-diagnose pas na de eerste opnamedag een `Baseline` krijgt (`start_dag_offset > 0`)
- **THEN** wordt deze in de EDA zichtbaar gemaakt als een later gestarte diagnose (en gedocumenteerd als aandachtspunt voor *data leakage* bij vroeg voorspellen)
