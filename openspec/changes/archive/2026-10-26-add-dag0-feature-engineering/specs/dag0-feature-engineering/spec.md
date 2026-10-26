## ADDED Requirements

### Requirement: Day-Zero Restricted Feature Derivation
Het systeem SHALL per `Opnamenummer` een featuretabel opleveren waarvan elke kolom uitsluitend is
afgeleid van metingen met `Meet_dag_van_opname == 0` en `Meetmoment == 'Baseline'`, zodat de
features overeenkomen met de informatie die op het moment van opname beschikbaar was.

#### Scenario: Diagnose die pas na dag 0 start telt niet mee
- **WHEN** een opname een NANDA-diagnose bevat waarvan de eerste `Baseline` op dag 3 is geregistreerd
- **THEN** telt die diagnose niet mee in `n_diagnoses_dag0` en dragen haar indicatoren niet bij aan
  `baseline_score_gem_dag0`, `baseline_score_min_dag0` of `n_indicatoren_onder_5_dag0`

#### Scenario: Opname zonder dag-0 metingen
- **WHEN** een opname geen enkele `Baseline`-meting op de eerste opnamedag heeft
- **THEN** blijft de opname in de featuretabel aanwezig met `heeft_dag0_meting == False`, tellingen
  op `0` en scorekolommen op `NaN`, zodat de opname bewust kan worden uitgesloten in plaats van
  stilzwijgend te verdwijnen

### Requirement: Care Plan Content as Model Features
Het systeem SHALL per opname 0/1-kolommen leveren voor de NANDA-diagnoses die op dag 0 liepen,
waarbij diagnoses die minder vaak dan een instelbare drempel voorkomen worden samengevoegd in
één restcategorie.

#### Scenario: Zeldzame diagnose valt in de restcategorie
- **WHEN** de dummies worden gebouwd met `min_voorkomens = 3` en een NANDA-diagnose komt in slechts
  één opname op dag 0 voor
- **THEN** krijgt die diagnose geen eigen kolom en wordt de opname gemarkeerd in `diag_overig`

### Requirement: Explicit Leakage Guard
Het systeem SHALL een controlefunctie bieden die een `ValueError` werpt zodra een featuretabel een
kolom bevat die is afgeleid van `Eindscore`-metingen, `Gezondheidswinst`, diagnoseduur of
opnamebrede totalen, met uitzondering van een expliciete witte lijst (`Opnameduur_dagen` als
doelvariabele, `Opnamenummer` en `Patientnr` als sleutels).

#### Scenario: Niet-veilige kolom wordt geblokkeerd
- **WHEN** een featuretabel de kolom `n_diagnoses_totaal` of `gem_gezondheidswinst` bevat
- **THEN** faalt de controle met een foutmelding die de betreffende kolomnaam noemt

#### Scenario: Schone dag-0 tabel komt door de controle
- **WHEN** de controle draait op een tabel met alleen `*_dag0`-kolommen, de sleutels en de
  doelvariabele `Opnameduur_dagen`
- **THEN** gaat de controle zonder fout door

### Requirement: Patient-Level Train/Test Split
Het systeem SHALL een splitsing leveren die unieke `Patientnr`-waarden over train en test verdeelt,
zodat alle opnames van dezelfde patiënt in hetzelfde deel terechtkomen.

#### Scenario: Patient met meerdere opnames blijft bij elkaar
- **WHEN** een patiënt meerdere `Opnamenummer`-waarden in de dataset heeft en de tabel wordt gesplitst
- **THEN** staan al die opnames in hetzelfde deel en is de doorsnede van de patiëntnummers in train
  en test leeg
