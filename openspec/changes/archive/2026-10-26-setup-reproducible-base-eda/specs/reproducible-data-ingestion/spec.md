## ADDED Requirements

### Requirement: Portable Excel Data Loading
Het systeem SHALL het HMC-NNN Excel-bestand (`Test datasheet NNN Minor.xlsx`) kunnen inladen via een relatief pad (`pathlib.Path`) dat zowel werkt vanuit de project-root als vanuit een `notebooks/` submap, zonder hardcoded gebruikerspaden.

#### Scenario: Notebook wordt uitgevoerd vanuit de notebooks map of project-root
- **WHEN** een student de data-import functie uitvoert in het notebook (vanuit `./` of `./notebooks/`)
- **THEN** vindt het script automatisch `Test datasheet NNN Minor.xlsx` en laadt het de rijen in een pandas DataFrame zonder `FileNotFoundError`

### Requirement: Column Normalization and Schema Validation
De data-import stap SHALL ruwe kolomnamen normaliseren naar consistente, code-vriendelijke kolomnamen (waaronder het hernoemen van `'RAPm vNandaNicNoc_Probleem'[Opnamenummer]` naar `Opnamenummer` en `Score oms` naar `Score_omschrijving`) en controleren of alle verplichte kolommen aanwezig zijn.

#### Scenario: Ruwe HMC-NNN Excel met DAX-achtige kolomnaam wordt ingeladen
- **WHEN** het Excel-bestand met kolom `'RAPm vNandaNicNoc_Probleem'[Opnamenummer]` wordt ingeladen
- **THEN** wordt de kolom hernoemd naar `Opnamenummer` en zijn alle 12 kernkolommen (`Patientnr`, `Opnamenummer`, `Diagnose`, `Indicator`, `MeetScore`, `Score_omschrijving`, `Gezondheidswinst`, `Meetdatum`, `Meettijd`, `Meetmoment`, `ICD10Code`, `ICD10Omschrijving`) direct aanspreekbaar

#### Scenario: Ontbrekende verplichte kolom in een nieuw bestand
- **WHEN** een bestand wordt ingeladen waarin een verplichte kolom (zoals `Meetdatum` of `Diagnose`) ontbreekt
- **THEN** geeft de validatiefunctie een duidelijke foutmelding met exact welke kolom ontbreekt

### Requirement: Date, Time, and Numeric Type Parsing
De data-import stap SHALL `Meetdatum` converteren naar een `datetime64[ns]` datum, een gecombineerde `Meet_datetime` (`Meetdatum` + `Meettijd`) aanmaken, en `MeetScore` evenals `Gezondheidswinst` converteren naar numerieke datatypes (`Int64` / `float64` met behoud van `NaN` voor lege `Gezondheidswinst` op `Baseline`).

#### Scenario: Datums en numerieke scores worden geparseerd
- **WHEN** de ruwe data wordt verwerkt door de preprocessing functie
- **THEN** is `Meetdatum` van het type `datetime64[ns]`, is `MeetScore` numeriek (1 t/m 5), en bevat `Gezondheidswinst` numerieke waarden bij `Eindscore` en `NaN` waar geen winst is ingevuld
