"""
01_clean_dataset.py
-------------------
Genera el dataset limpio de mora a partir de dos archivos Excel:
  - ReportedeAntiguedaddeCartera_*.xlsx  → variables de mora
  - CapturadeAcreditados_*.xlsx          → tasa de interés (complementario)

Uso:
    python scripts/01_clean_dataset.py

Salida:
    outputs/dataset_mora.csv

Columnas del dataset limpio:
    id_acreditado  — Código único del cliente
    ciclo          — Número de renovación del crédito (referencia)
    monto          — Cantidad Prestada en MXN
    dias_mora      — Días transcurridos desde el primer incumplimiento
    plazo_meses    — Plazo del crédito convertido a meses
    tasa_interes   — Tasa de interés anual (%) — NaN para 2 créditos sin match
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "outputs"
OUT_PATH = OUT_DIR / "dataset_mora.csv"

FACTORES = {
    "Mensual":    1.0,
    "Quincenal":  0.5,
    "Catorcenal": 14 / 30.44,
    "Semanal":     7 / 30.44,
}


def encontrar_excel(patron: str) -> Path:
    archivos = sorted(DATA_DIR.glob(patron), key=lambda f: f.stat().st_mtime)
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún archivo '{patron}' en {DATA_DIR}")
    return archivos[-1]


def construir_dataset() -> pd.DataFrame:
    # ── Archivo principal: antigüedad de cartera ───────────────────────────────
    path_mora = encontrar_excel("ReportedeAntiguedad*.xlsx")
    print(f"[01_clean_dataset] Archivo mora      : {path_mora.name}")
    df = pd.read_excel(path_mora, sheet_name=0)
    df.columns = [c.replace("\n", " ") for c in df.columns]
    df = df[df.iloc[:, 29] == "Entregado"].copy()

    result = pd.DataFrame()
    result["id_acreditado"] = df.iloc[:, 6].astype(int)
    result["ciclo"]         = df.iloc[:, 7].astype(int)
    result["monto"]         = pd.to_numeric(df.iloc[:, 12], errors="coerce")
    result["dias_mora"]     = pd.to_numeric(df.iloc[:, 13], errors="coerce").fillna(0).astype(int)

    plazo        = pd.to_numeric(df.iloc[:, 14], errors="coerce")
    periodicidad = df.iloc[:, 15].astype(str).str.strip()
    factor       = periodicidad.map(FACTORES)
    sin_factor   = periodicidad[factor.isna()].unique()
    if len(sin_factor) > 0:
        print(f"  AVISO: periodicidades sin factor definido: {sin_factor}")
    result["plazo_meses"] = (plazo * factor).round(2)

    antes = len(result)
    result = result.dropna(subset=["monto", "plazo_meses"]).reset_index(drop=True)
    if antes - len(result) > 0:
        print(f"  AVISO: {antes - len(result)} registros descartados por nulos en monto/plazo")

    # ── Archivo complementario: captura de acreditados (tasa de interés) ───────
    path_acred = encontrar_excel("CapturadeAcreditados*.xlsx")
    print(f"[01_clean_dataset] Archivo tasa      : {path_acred.name}")
    df_acred = pd.read_excel(path_acred, sheet_name=0)
    df_acred.columns = [c.replace("\n", " ") for c in df_acred.columns]
    df_acred = df_acred[df_acred.iloc[:, 38] == "Entregado"].copy()

    # Deduplicar: IDs 1055 y 3824 aparecen dos veces — conservar primera fila
    df_tasa = (df_acred.iloc[:, [3, 39]]
               .rename(columns={df_acred.columns[3]: "id_acreditado",
                                df_acred.columns[39]: "tasa_interes"})
               .drop_duplicates(subset="id_acreditado", keep="first")
               .reset_index(drop=True))
    df_tasa["id_acreditado"] = df_tasa["id_acreditado"].astype(int)

    # ── Join (left): 2 créditos sin match quedan con tasa NaN ─────────────────
    result = result.merge(df_tasa, on="id_acreditado", how="left")
    sin_tasa = result["tasa_interes"].isna().sum()
    if sin_tasa > 0:
        ids_sin = result.loc[result["tasa_interes"].isna(), "id_acreditado"].tolist()
        print(f"  INFO: {sin_tasa} créditos sin tasa (excluidos solo del análisis de tasa): {ids_sin}")

    return result


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df_clean = construir_dataset()
    df_clean.to_csv(OUT_PATH, index=False)

    n_total  = len(df_clean)
    n_mora   = (df_clean["dias_mora"] > 0).sum()
    pct_mora = n_mora / n_total * 100

    print(f"[01_clean_dataset] Dataset guardado : {OUT_PATH.name}")
    print(f"[01_clean_dataset] Total créditos   : {n_total}")
    print(f"[01_clean_dataset] En mora (>0 días): {n_mora}  ({pct_mora:.1f}%)")
    print(f"[01_clean_dataset] Sin mora          : {n_total - n_mora}  ({100 - pct_mora:.1f}%)")
    print(f"[01_clean_dataset] Columnas          : {list(df_clean.columns)}")


if __name__ == "__main__":
    main()
