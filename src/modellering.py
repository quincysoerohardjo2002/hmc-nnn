from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DOELVARIABELE = "Opnameduur_dagen"
GROEPSKOLOM = "Patientnr"

# Sleutels en labels horen nooit bij de features.
UITGESLOTEN_KOLOMMEN = (
    "Opnamenummer",
    "Patientnr",
    "ICD10Code",
    "ICD10Omschrijving",
    "Opnameduur_dagen",
)

ICD10_KOLOMMEN = ("icd10_hoofdcode",)

FEATURESETS = ("icd10", "nanda_noc", "beide")


def _nanda_noc_kolommen(tabel: pd.DataFrame) -> List[str]:
    return [
        kolom
        for kolom in tabel.columns
        if kolom not in UITGESLOTEN_KOLOMMEN
        and kolom not in ICD10_KOLOMMEN
        and (kolom.endswith("_dag0") or kolom.startswith("diag_") or kolom == "heeft_dag0_meting")
    ]


def bouw_featureset(tabel: pd.DataFrame, naam: str) -> Tuple[pd.DataFrame, List[str], List[str]]:
    if naam not in FEATURESETS:
        raise ValueError(f"Onbekende featureset '{naam}'. Kies uit: {', '.join(FEATURESETS)}.")

    categorisch = [k for k in ICD10_KOLOMMEN if k in tabel.columns]
    numeriek = _nanda_noc_kolommen(tabel)

    if naam == "icd10":
        numeriek = []
    elif naam == "nanda_noc":
        categorisch = []

    kolommen = [*categorisch, *numeriek]
    if not kolommen:
        raise ValueError(f"Featureset '{naam}' levert geen enkele kolom op in deze tabel.")

    X = tabel[kolommen].copy()
    # Booleans als 0/1, zodat de imputer en het model er zonder waarschuwing mee rekenen.
    for kolom in numeriek:
        if X[kolom].dtype == bool:
            X[kolom] = X[kolom].astype("int64")

    return X, numeriek, categorisch


def maak_pipeline(model, numerieke_kolommen: Sequence[str], categorische_kolommen: Sequence[str]) -> Pipeline:
    stappen = []
    if numerieke_kolommen:
        stappen.append(("num", SimpleImputer(strategy="median"), list(numerieke_kolommen)))
    if categorische_kolommen:
        stappen.append(
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), list(categorische_kolommen))
        )

    voorbewerking = ColumnTransformer(stappen, remainder="drop")
    return Pipeline([("voorbewerking", voorbewerking), ("model", model)])


def evalueer_model(tabel: pd.DataFrame, featureset: str, model) -> Dict[str, object]:
    X, numeriek, categorisch = bouw_featureset(tabel, featureset)
    y = tabel[DOELVARIABELE].to_numpy(dtype=float)
    groepen = tabel[GROEPSKOLOM].to_numpy()

    pipeline = maak_pipeline(model, numeriek, categorisch)
    splitser = LeaveOneGroupOut()

    # cross_val_predict verzamelt per fold de voorspelling voor de weggelaten patient(en);
    # de metrieken rekenen we daarna een keer over de volledige vector.
    voorspeld = cross_val_predict(pipeline, X, y, cv=splitser, groups=groepen)

    return {
        "featureset": featureset,
        "n_features": X.shape[1],
        "n_folds": splitser.get_n_splits(X, y, groepen),
        "MAE_dagen": float(mean_absolute_error(y, voorspeld)),
        "RMSE_dagen": float(root_mean_squared_error(y, voorspeld)),
        "R2": float(r2_score(y, voorspeld)),
        "werkelijk": y,
        "voorspeld": voorspeld,
    }


def vergelijk_modellen(
    tabel: pd.DataFrame,
    modellen: Dict[str, object],
    featuresets: Iterable[str] = FEATURESETS,
) -> Tuple[pd.DataFrame, Dict[Tuple[str, str], Dict[str, object]]]:
    rijen = []
    details: Dict[Tuple[str, str], Dict[str, object]] = {}

    for modelnaam, model in modellen.items():
        for featureset in featuresets:
            # Elke combinatie krijgt een eigen, ongetrainde kopie van het model.
            uitkomst = evalueer_model(tabel, featureset, clone(model))
            details[(modelnaam, featureset)] = uitkomst
            rijen.append(
                {
                    "model": modelnaam,
                    "featureset": featureset,
                    "n_features": uitkomst["n_features"],
                    "MAE_dagen": round(uitkomst["MAE_dagen"], 2),
                    "RMSE_dagen": round(uitkomst["RMSE_dagen"], 2),
                    "R2": round(uitkomst["R2"], 3),
                }
            )

    resultaten = pd.DataFrame(rijen).sort_values("MAE_dagen").reset_index(drop=True)
    return resultaten, details
