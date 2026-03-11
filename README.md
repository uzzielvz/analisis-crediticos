# Análisis de Mora Crediticia — Cartera Estado México

Análisis estadístico de la relación entre las variables de crédito (monto, plazo, tasa de interés) y los días de mora. Cartera activa al 06/03/2026.

---

## Cómo ejecutar

### Opción A — Google Colab (sin instalar nada)

1. Abre [colab.research.google.com](https://colab.research.google.com)
2. **Archivo → Abrir notebook → GitHub**
3. Pega: `uzzielvz/analisis-crediticos`
4. Selecciona `notebook/analisis_mora.ipynb`
5. **Ejecutar todo** (`Ctrl+F9`)

La primera celda clona el repositorio automáticamente. No se necesita configurar nada más.

### Opción B — Local

```bash
git clone https://github.com/uzzielvz/analisis-crediticos.git
cd analisis-crediticos
pip install pandas openpyxl matplotlib scipy statsmodels scikit-learn jupyter
jupyter notebook notebook/analisis_mora.ipynb
```

---

## Estructura

```
data/
  ReportedeAntiguedaddeCartera_060326.xlsx   # Fuente principal (mora)
  CapturadeAcreditados_100326.xlsx            # Fuente complementaria (tasa)
notebook/
  analisis_mora.ipynb                         # Notebook principal
outputs/
  dataset_mora.csv                            # Dataset limpio generado
scripts/
  01_clean_dataset.py                         # Genera el CSV desde los Excel
  build_notebook.py                           # Regenera el notebook (desarrollo)
```

---

## Variables analizadas

| Variable | Descripción | Fuente |
|---|---|---|
| `monto` | Cantidad prestada (MXN) | Reporte antigüedad |
| `plazo_meses` | Plazo convertido a meses | Reporte antigüedad |
| `tasa_interes` | Tasa de interés anual (%) | Captura acreditados |
| `dias_mora` | Días desde el primer incumplimiento | Reporte antigüedad |

---

## Actualizar para un nuevo corte

1. Agrega los nuevos Excel a `data/`
2. Borra `outputs/dataset_mora.csv`
3. Ejecuta el notebook — regenera el CSV automáticamente
4. Sube los cambios: `git add data/ outputs/dataset_mora.csv && git push`
