## Why

Voor het HMC-NNN Datalab project onderzoeken we met een studententeam hoe gestandaardiseerde verpleegkundige zorgplandata (NANDA-I diagnoses en NOC-uitkomstindicatoren) en medische opname-indicaties (ICD-10) gebruikt kunnen worden om de opnameduur (Length of Stay - LOS) van ziekenhuispatiënten te voorspellen. Er is momenteel nog geen gestandaardiseerde, reproduceerbare manier om de dataset in te laden, opnameduur en diagnoseduur per zorgplan af te leiden, en de basis-EDA uit te voeren die alle groepsleden als gedeeld startpunt kunnen gebruiken.

## What Changes

- Toevoegen van een reproduceerbare Python-omgevingsconfiguratie (`requirements.txt`) zodat alle medestudenten exact dezelfde pakketten (zoals `pandas`, `openpyxl`, `matplotlib`, `seaborn`, `scipy`, `jupyter`) kunnen gebruiken.
- Opzetten van een herbruikbare data-import en preprocessing stap die het ruwe Excel-bestand (`Test datasheet NNN Minor.xlsx` en latere HMC-exports) inlaadt, kolomnamen opschoont, Excel-datums/tijden omzet naar echte `datetime`-objecten en valideert op verwachte kolommen.
- Toevoegen van een gestandaardiseerde aggregatielaag die op basis van `Opnamenummer` (het zorgplan) de totale opnameduur (`max(Meetdatum) - min(Meetdatum)`), individuele diagnoseduur (`Eindscore` datum min `Baseline` datum per NANDA-diagnose), en het aantal diagnoses/indicatoren per zorgplan berekent.
- Creëren van een reproduceerbare Jupyter Notebook (`notebooks/01_base_eda_hmc_nnn.ipynb`) met de 5 kernanalyses van de basis-EDA:
  1. **Datakwaliteit & Zorgplan-integriteit**: controle op ontbrekende waarden, wees-metingen (enkel Baseline of enkel Eindscore) en herhaalde metingen.
  2. **Opnameduur vs. Diagnoseduur**: verdeling van de totale opnameduur per opname en de doorlooptijd van individuele NANDA-diagnoses.
  3. **Zorgplan-complexiteit vs. Opnameduur**: relatie tussen het aantal NANDA-diagnoses / NOC-indicatoren in een zorgplan en de totale opnameduur (inclusief onderscheid tussen alle diagnoses en actieve klachten met score < 5).
  4. **Tijdlijn & Startmoment van Diagnoses**: onderscheid tussen diagnoses die bij aanvang van de opname (Dag 0) starten versus diagnoses die later tijdens de opname ontstaan (en het risico op data leakage bij voorspellen).
  5. **Medische (ICD-10) vs. Verpleegkundige (NANDA/NOC) verklaringskracht**: vergelijking van verschillen in opnameduur en zorgplan-inhoud binnen dezelfde ICD-10 hoofddiagnose.

## Capabilities

### New Capabilities
- `reproducible-data-ingestion`: Gestandaardiseerd inladen, valideren, opschonen van kolomnamen en converteren van datum-/tijdvelden uit het HMC-NNN Excel-databestand voor alle teamleden.
- `careplan-los-eda`: Berekenen van zorgplan-aggregaties (totale opnameduur, individuele diagnoseduur, aantal NANDA-diagnoses en NOC-indicatoren) en uitvoeren van de 5 basis-EDA analyses in een reproduceerbaar Jupyter Notebook.

### Modified Capabilities
<!-- Geen bestaande capabilities worden gewijzigd. -->

## Impact

- **Nieuwe bestanden**:
  - `requirements.txt` voor reproduceerbare installatie van dependencies door klasgenoten.
  - `notebooks/01_base_eda_hmc_nnn.ipynb` als het centrale, gedocumenteerde EDA-notebook.
- **Data-afhankelijkheden**: Leest `Test datasheet NNN Minor.xlsx` (relatief pad vanuit de project-root zodat het op elke laptop werkt zonder hardcoded gebruikerspaden) zonder het bronbestand aan te passen.
