from __future__ import annotations

import re
from typing import Iterable, Tuple

import numpy as np
import pandas as pd

# NOC: score 5 staat voor 'geen probleem / niet beperkt'.
GEEN_PROBLEEM_SCORE = 5

# Kolomnaam-fragmenten die wijzen op informatie die op dag 0 nog niet bestond.
LEAKAGE_FRAGMENTEN = ("eind", "gezondheidswinst", "duur", "totaal", "later", "compleet")

# Sleutels en de doelvariabele mogen zo'n fragment wel bevatten.
LEAKAGE_WITTE_LIJST = ("Opnamenummer", "Patientnr", "Opnameduur_dagen")

TELKOLOMMEN_DAG0 = [
    "n_metingen_dag0",
    "n_diagnoses_dag0",
    "n_indicatoren_dag0",
    "n_diagnoses_actief_dag0",
    "n_indicatoren_onder_5_dag0",
]

SCOREKOLOMMEN_DAG0 = [
    "baseline_score_gem_dag0",
    "baseline_score_min_dag0",
    "pct_score_5_dag0",
]


def selecteer_dag0_metingen(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["Meet_dag_van_opname"] == 0) & (df["Meetmoment"] == "Baseline")]


def build_dag0_features(df: pd.DataFrame) -> pd.DataFrame:
    opname_basis = df.groupby("Opnamenummer").agg(
        Patientnr=("Patientnr", "first"),
        ICD10Code=("ICD10Code", "first"),
        ICD10Omschrijving=("ICD10Omschrijving", "first"),
        Opnameduur_dagen=("Opnameduur_dagen", "first"),
    )
    opname_basis["icd10_hoofdcode"] = opname_basis["ICD10Code"].astype(str).str.slice(0, 3)

    dag0 = selecteer_dag0_metingen(df)
    onder_drempel = dag0[dag0["MeetScore"] < GEEN_PROBLEEM_SCORE]

    kern = dag0.groupby("Opnamenummer").agg(
        n_metingen_dag0=("MeetScore", "size"),
        n_diagnoses_dag0=("Diagnose", "nunique"),
        n_indicatoren_dag0=("Indicator", "nunique"),
        baseline_score_gem_dag0=("MeetScore", "mean"),
        baseline_score_min_dag0=("MeetScore", "min"),
    )
    kern["n_diagnoses_actief_dag0"] = onder_drempel.groupby("Opnamenummer")["Diagnose"].nunique()
    kern["n_indicatoren_onder_5_dag0"] = onder_drempel.groupby("Opnamenummer")["Indicator"].nunique()
    kern["pct_score_5_dag0"] = (
        dag0.assign(_is_vijf=lambda t: (t["MeetScore"] == GEEN_PROBLEEM_SCORE).astype(float))
        .groupby("Opnamenummer")["_is_vijf"]
        .mean()
        * 100.0
    )

    # Opnames zonder dag-0 metingen verdwijnen uit de groupby; die horen hier wel thuis
    # met een expliciete nul, zodat ze bewust uitgesloten kunnen worden.
    kern = kern.reindex(opname_basis.index)
    kern[TELKOLOMMEN_DAG0] = kern[TELKOLOMMEN_DAG0].fillna(0).astype("int64")
    kern[SCOREKOLOMMEN_DAG0] = kern[SCOREKOLOMMEN_DAG0].astype("float64")
    kern["heeft_dag0_meting"] = kern["n_metingen_dag0"] > 0

    features = opname_basis.join(kern)
    kolomvolgorde = [
        "Patientnr",
        "ICD10Code",
        "ICD10Omschrijving",
        "icd10_hoofdcode",
        "heeft_dag0_meting",
        *TELKOLOMMEN_DAG0,
        *SCOREKOLOMMEN_DAG0,
        "Opnameduur_dagen",
    ]
    return features[kolomvolgorde].reset_index()


def _kolomnaam(diagnose: str, prefix: str) -> str:
    schoon = re.sub(r"[^a-z0-9]+", "_", str(diagnose).lower()).strip("_")
    return f"{prefix}{schoon}"


def build_dag0_diagnose_dummies(
    df: pd.DataFrame, min_voorkomens: int = 1, prefix: str = "diag_"
) -> pd.DataFrame:
    dag0 = selecteer_dag0_metingen(df)
    paren = dag0[["Opnamenummer", "Diagnose"]].drop_duplicates()

    voorkomens = paren["Diagnose"].value_counts()
    behouden = set(voorkomens[voorkomens >= min_voorkomens].index)
    paren = paren.assign(
        kolom=[
            _kolomnaam(diagnose, prefix) if diagnose in behouden else f"{prefix}overig"
            for diagnose in paren["Diagnose"]
        ]
    )

    dummies = pd.crosstab(paren["Opnamenummer"], paren["kolom"]).clip(upper=1)
    alle_opnames = pd.Index(sorted(df["Opnamenummer"].unique()), name="Opnamenummer")
    dummies = dummies.reindex(alle_opnames, fill_value=0).astype("int64")
    dummies.columns.name = None
    return dummies.reset_index()


def controleer_geen_leakage(
    tabel: pd.DataFrame, extra_toegestaan: Iterable[str] = ()
) -> bool:
    toegestaan = {naam.lower() for naam in (*LEAKAGE_WITTE_LIJST, *extra_toegestaan)}

    verdacht = []
    for kolom in tabel.columns:
        if str(kolom).lower() in toegestaan:
            continue
        geraakt = [f for f in LEAKAGE_FRAGMENTEN if f in str(kolom).lower()]
        if geraakt:
            verdacht.append(f"  - {kolom} (bevat: {', '.join(geraakt)})")

    if verdacht:
        raise ValueError(
            "Mogelijke data leakage: deze kolommen lijken afgeleid van informatie die op "
            "dag 0 nog niet bestond.\n"
            + "\n".join(verdacht)
            + "\nIs de kolom toch veilig? Geef hem dan mee via extra_toegestaan."
        )
    return True


def split_op_patient(
    tabel: pd.DataFrame, test_fractie: float = 0.25, seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if "Patientnr" not in tabel.columns:
        raise ValueError("Tabel heeft geen kolom 'Patientnr'; splitsen op patient kan niet.")
    if not 0 < test_fractie < 1:
        raise ValueError(f"test_fractie moet tussen 0 en 1 liggen, niet {test_fractie}.")

    patienten = np.sort(tabel["Patientnr"].dropna().unique())
    if len(patienten) < 2:
        raise ValueError("Er zijn minder dan twee patienten; splitsen heeft geen zin.")

    rng = np.random.default_rng(seed)
    door_elkaar = rng.permutation(patienten)
    n_test = int(round(len(door_elkaar) * test_fractie))
    n_test = min(max(n_test, 1), len(door_elkaar) - 1)

    test_patienten = set(door_elkaar[:n_test])
    in_test = tabel["Patientnr"].isin(test_patienten)
    return tabel.loc[~in_test].copy(), tabel.loc[in_test].copy()
