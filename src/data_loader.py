from __future__ import annotations

from pathlib import Path
from typing import Optional, Union
import warnings
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd

DEFAULT_FILENAME = "Test datasheet NNN Minor.xlsx"

COLUMN_RENAME_MAP = {
    "'RAPm vNandaNicNoc_Probleem'[Opnamenummer]": "Opnamenummer",
    "Score oms": "Score_omschrijving",
}

REQUIRED_COLUMNS = [
    "Patientnr",
    "Opnamenummer",
    "Diagnose",
    "Indicator",
    "MeetScore",
    "Score_omschrijving",
    "Gezondheidswinst",
    "Meetdatum",
    "Meettijd",
    "Meetmoment",
    "ICD10Code",
    "ICD10Omschrijving",
]


def resolve_data_path(file_path: Optional[Union[str, Path]] = None) -> Path:
    if file_path is not None:
        candidate = Path(file_path)
        if candidate.is_file():
            return candidate.resolve()

    filename = Path(file_path).name if file_path is not None else DEFAULT_FILENAME
    search_roots = [
        Path.cwd(),
        Path.cwd().parent,
        Path(__file__).resolve().parent.parent,
    ]
    for root in search_roots:
        for candidate in (root / filename, root / "data" / filename):
            if candidate.is_file():
                return candidate.resolve()

    raise FileNotFoundError(
        f"Kan databestand '{filename}' niet vinden in {[str(r) for r in search_roots]}"
    )


def _read_xlsx_fallback(path: Path) -> pd.DataFrame:
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(path, "r") as zf:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            strings = ["".join(si.itertext()) for si in ss_root.findall(f".//{ns}si")]

        sheet_root = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
        rows = sheet_root.findall(f".//{ns}row")

        parsed_rows: list[dict[str, str]] = []
        for row in rows:
            row_dict: dict[str, str] = {}
            for cell in row.findall(f"{ns}c"):
                col_letters = "".join(ch for ch in cell.attrib.get("r", "") if ch.isalpha())
                cell_type = cell.attrib.get("t")
                v_node = cell.find(f"{ns}v")
                val = v_node.text if v_node is not None and v_node.text is not None else ""
                if cell_type == "s" and val.isdigit():
                    val = strings[int(val)]
                row_dict[col_letters] = val
            parsed_rows.append(row_dict)

    if not parsed_rows:
        return pd.DataFrame()

    header_map = parsed_rows[0]
    col_order = list(header_map.keys())
    records = [
        {header_map[col]: r.get(col, "") for col in col_order}
        for r in parsed_rows[1:]
    ]
    return pd.DataFrame(records)


def read_raw_excel(file_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    resolved = resolve_data_path(file_path)
    try:
        return pd.read_excel(resolved)
    except ImportError:
        warnings.warn(
            "openpyxl is niet geinstalleerd; er wordt teruggevallen op een beperkte "
            "XML-lezer. Installeer de dependencies met: pip install -r requirements.txt",
            RuntimeWarning,
            stacklevel=2,
        )
        return _read_xlsx_fallback(resolved)


def load_and_clean_hmc_data(file_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    df = read_raw_excel(file_path).copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns=COLUMN_RENAME_MAP)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Ontbrekende verplichte kolommen in dataset: {missing_cols}. "
            f"Gevonden kolommen: {list(df.columns)}"
        )

    df = df.replace("", np.nan)

    df["Patientnr"] = pd.to_numeric(df["Patientnr"], errors="coerce").astype("Int64")
    df["Opnamenummer"] = pd.to_numeric(df["Opnamenummer"], errors="coerce").astype("Int64")
    df["MeetScore"] = pd.to_numeric(df["MeetScore"], errors="coerce").astype("Int64")
    df["Gezondheidswinst"] = pd.to_numeric(df["Gezondheidswinst"], errors="coerce").astype("float64")

    if pd.api.types.is_datetime64_any_dtype(df["Meetdatum"]):
        df["Meetdatum"] = pd.to_datetime(df["Meetdatum"]).dt.normalize()
    else:
        num_dates = pd.to_numeric(df["Meetdatum"], errors="coerce")
        if num_dates.notna().all() and (num_dates > 20000).all():
            df["Meetdatum"] = pd.to_datetime(num_dates, unit="D", origin="1899-12-30").dt.normalize()
        else:
            df["Meetdatum"] = pd.to_datetime(df["Meetdatum"], errors="coerce").dt.normalize()

    df["Meettijd"] = df["Meettijd"].astype(str).str.strip()
    time_delta = pd.to_timedelta(df["Meettijd"] + ":00", errors="coerce")
    df["Meet_datetime"] = df["Meetdatum"] + time_delta.fillna(pd.Timedelta(0))

    opname_bounds = df.groupby("Opnamenummer")["Meetdatum"].agg(
        Opname_startdatum="min",
        Opname_einddatum="max",
    )
    df = df.merge(opname_bounds, on="Opnamenummer", how="left")
    df["Opnameduur_dagen"] = (df["Opname_einddatum"] - df["Opname_startdatum"]).dt.days
    df["Meet_dag_van_opname"] = (df["Meetdatum"] - df["Opname_startdatum"]).dt.days

    return df


def build_diagnosis_table(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    grouped = df.groupby(["Opnamenummer", "Patientnr", "ICD10Code", "ICD10Omschrijving", "Diagnose"], dropna=False)

    for (opn, pat, icd_code, icd_desc, diag), grp in grouped:
        opname_start = grp["Opname_startdatum"].iloc[0]
        opname_eind = grp["Opname_einddatum"].iloc[0]
        opnameduur = grp["Opnameduur_dagen"].iloc[0]

        base_grp = grp[grp["Meetmoment"] == "Baseline"]
        end_grp = grp[grp["Meetmoment"] == "Eindscore"]

        has_base = len(base_grp) > 0
        has_end = len(end_grp) > 0

        if has_base and has_end:
            status = "Compleet (Baseline + Eindscore)"
        elif has_base:
            status = "Enkel Baseline"
        elif has_end:
            status = "Enkel Eindscore"
        else:
            status = "Overig"

        diag_start = base_grp["Meetdatum"].min() if has_base else grp["Meetdatum"].min()
        diag_eind = end_grp["Meetdatum"].max() if has_end else grp["Meetdatum"].max()

        diag_duur = (
            int((diag_eind - diag_start).days)
            if (has_base and has_end and pd.notna(diag_start) and pd.notna(diag_eind))
            else np.nan
        )
        start_dag_offset = (
            int((diag_start - opname_start).days)
            if (has_base and pd.notna(diag_start) and pd.notna(opname_start))
            else np.nan
        )

        base_scores = base_grp["MeetScore"].dropna()
        end_scores = end_grp["MeetScore"].dropna()
        winst_vals = end_grp["Gezondheidswinst"].dropna()

        records.append(
            {
                "Opnamenummer": opn,
                "Patientnr": pat,
                "ICD10Code": icd_code,
                "ICD10Omschrijving": icd_desc,
                "Diagnose": diag,
                "Compleetheid": status,
                "Aantal_indicatoren": grp["Indicator"].nunique(),
                "Aantal_meting_rijen": len(grp),
                "Aantal_baseline_datums": base_grp["Meetdatum"].nunique(),
                "Aantal_eindscore_datums": end_grp["Meetdatum"].nunique(),
                "Diagnose_startdatum": diag_start if has_base else pd.NaT,
                "Diagnose_einddatum": diag_eind if has_end else pd.NaT,
                "Diagnoseduur_dagen": diag_duur,
                "Start_dag_offset": start_dag_offset,
                "Gestart_op_dag0": bool(start_dag_offset == 0) if pd.notna(start_dag_offset) else False,
                "Baseline_min_score": float(base_scores.min()) if len(base_scores) > 0 else np.nan,
                "Baseline_mean_score": float(base_scores.mean()) if len(base_scores) > 0 else np.nan,
                "Heeft_actieve_klacht_baseline": bool((base_scores < 5).any()) if len(base_scores) > 0 else False,
                "Eind_mean_score": float(end_scores.mean()) if len(end_scores) > 0 else np.nan,
                "Gem_gezondheidswinst": float(winst_vals.mean()) if len(winst_vals) > 0 else np.nan,
                "Opname_startdatum": opname_start,
                "Opname_einddatum": opname_eind,
                "Opnameduur_dagen": int(opnameduur),
            }
        )

    return pd.DataFrame(records).sort_values(["Opnamenummer", "Diagnose"]).reset_index(drop=True)


def build_admission_table(df: pd.DataFrame, df_diagnoses: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    if df_diagnoses is None:
        df_diagnoses = build_diagnosis_table(df)

    records = []
    for opn, grp in df.groupby("Opnamenummer"):
        diag_grp = df_diagnoses[df_diagnoses["Opnamenummer"] == opn]
        base_grp = grp[grp["Meetmoment"] == "Baseline"]
        end_grp = grp[grp["Meetmoment"] == "Eindscore"]

        opname_start = grp["Opname_startdatum"].iloc[0]
        opname_eind = grp["Opname_einddatum"].iloc[0]
        los_days = int(grp["Opnameduur_dagen"].iloc[0])

        base_scores = base_grp["MeetScore"].dropna()
        winst_vals = end_grp["Gezondheidswinst"].dropna()

        records.append(
            {
                "Opnamenummer": int(opn),
                "Patientnr": int(grp["Patientnr"].iloc[0]),
                "ICD10Code": grp["ICD10Code"].iloc[0],
                "ICD10Omschrijving": grp["ICD10Omschrijving"].iloc[0],
                "Opname_startdatum": opname_start,
                "Opname_einddatum": opname_eind,
                "Opnameduur_dagen": los_days,
                "Is_dagopname": bool(los_days == 0),
                "n_diagnoses_totaal": int(diag_grp["Diagnose"].nunique()),
                "n_diagnoses_dag0": int(diag_grp["Gestart_op_dag0"].sum()),
                "n_diagnoses_later_gestart": int((diag_grp["Start_dag_offset"] > 0).sum()),
                "n_diagnoses_actief_baseline": int(diag_grp["Heeft_actieve_klacht_baseline"].sum()),
                "n_diagnoses_compleet": int((diag_grp["Compleetheid"] == "Compleet (Baseline + Eindscore)").sum()),
                "n_indicatoren_totaal": int(grp["Indicator"].nunique()),
                "n_metingen_totaal": int(len(grp)),
                "baseline_score_gemiddeld": float(base_scores.mean()) if len(base_scores) > 0 else np.nan,
                "baseline_score_min": float(base_scores.min()) if len(base_scores) > 0 else np.nan,
                "aantal_indicatoren_score_onder_5": int((base_scores < 5).sum()) if len(base_scores) > 0 else 0,
                "pct_baseline_score_5": float((base_scores == 5).mean() * 100.0) if len(base_scores) > 0 else np.nan,
                "gem_gezondheidswinst": float(winst_vals.mean()) if len(winst_vals) > 0 else np.nan,
            }
        )

    return pd.DataFrame(records).sort_values("Opnamenummer").reset_index(drop=True)
