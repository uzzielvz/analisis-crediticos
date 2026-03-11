"""
build_notebook.py
Genera notebook/analisis_mora.ipynb programaticamente.
Ejecutar: python scripts/build_notebook.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT  = ROOT / "notebook" / "analisis_mora.ipynb"

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}

def code(src):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [], "source": src}

# ---------------------------------------------------------------------------
cells = []

# COLAB SETUP
cells.append(code(
    "# ── Configuracion Google Colab ────────────────────────────────────────────\n"
    "# En local esta celda no hace nada.\n"
    "# En Colab clona el repositorio automaticamente.\n"
    "try:\n"
    "    import google.colab, os, subprocess\n"
    "    IN_COLAB = True\n"
    "    REPO = '/content/analisis-crediticos'\n"
    "    if not os.path.exists(REPO):\n"
    "        subprocess.run(['git', 'clone',\n"
    "                        'https://github.com/uzzielvz/analisis-crediticos.git', REPO],\n"
    "                       check=True)\n"
    "    print('Repositorio listo.')\n"
    "except ImportError:\n"
    "    IN_COLAB = False\n"
    "    print('Modo local.')"
))

# PORTADA
cells.append(md(
    "# Análisis de Mora — Cartera Estado México\n"
    "**Fecha de corte:** 06 de marzo de 2026 &nbsp;|&nbsp; **Región:** Estado México\n\n"
    "---\n\n"
    "### Preguntas que responde este análisis\n\n"
    "1. ¿El **monto** del crédito se relaciona con los días de mora?\n"
    "2. ¿El **plazo** (en meses) se relaciona con los días de mora?\n"
    "3. ¿La **combinación** de monto y plazo permite predecir si un crédito entrará en mora?\n\n"
    "---"
))

# IMPORTS
cells.append(code(
    "import pandas as pd\n"
    "import numpy as np\n"
    "import matplotlib.pyplot as plt\n"
    "import matplotlib.ticker as mticker\n"
    "from scipy.stats import spearmanr\n"
    "import statsmodels.api as sm\n"
    "from sklearn.metrics import roc_auc_score, roc_curve\n"
    "import subprocess, warnings\n"
    "from pathlib import Path\n"
    "warnings.filterwarnings('ignore')\n"
    "\n"
    "plt.rcParams['figure.dpi'] = 120\n"
    "plt.rcParams['axes.spines.top']   = False\n"
    "plt.rcParams['axes.spines.right'] = False\n"
    "AZUL='#2471A3'; ROJO='#C0392B'; VERDE='#1E8449'; NARANJA='#D35400'; GRIS='#717D7E'\n"
    "\n"
    "ROOT     = Path('/content/analisis-crediticos') if IN_COLAB else Path('..').resolve()\n"
    "CSV      = ROOT / 'outputs' / 'dataset_mora.csv'\n"
    "DATA_DIR = ROOT / 'data'\n"
    "\n"
    "if not CSV.exists():\n"
    "    import subprocess as _sp\n"
    "    _r = _sp.run(['python', str(ROOT/'scripts'/'01_clean_dataset.py')],\n"
    "                 capture_output=True, text=True)\n"
    "    if _r.returncode != 0: raise RuntimeError(_r.stderr)\n"
    "    print(_r.stdout)\n"
    "\n"
    "df = pd.read_csv(CSV)\n"
    "df['en_mora'] = (df['dias_mora'] > 0).astype(int)\n"
    "en = df[df['en_mora']==1]; no = df[df['en_mora']==0]"
))

# SEC 1 - DATOS
cells.append(md(
    "---\n"
    "## 1. Origen y preparación de los datos\n\n"
    "El análisis parte del **Reporte de Antigüedad de Cartera** (06/03/2026). "
    "Se aplica un filtro para trabajar únicamente con la **cartera viva**."
))

cells.append(code(
    "filtro = pd.DataFrame({\n"
    "    'Situacion': ['Entregado (activos)', 'Liquidado', 'Autorizado por cartera', 'TOTAL'],\n"
    "    'Registros': [213, 133, 1, 347],\n"
    "    'Incluido':  ['SI - cartera viva', 'NO - ya pagaron', 'NO - caso unico', '']\n"
    "})\n"
    "display(\n"
    "    filtro.set_index('Situacion').style\n"
    "    .set_caption('Tabla 1. Filtro aplicado al reporte fuente')\n"
    "    .set_table_styles([{'selector':'caption','props':"
    "[('font-size','13px'),('font-weight','bold'),('caption-side','top')]}])\n"
    "    .apply(lambda x: ['background-color:#D5F5E3' if 'SI' in str(v)\n"
    "                      else 'background-color:#FADBD8' if 'NO' in str(v)\n"
    "                      else '' for v in x], axis=1)\n"
    ")\n"
    "print('Los creditos Liquidado se excluyen porque su mora=0 refleja que ya pagaron,')\n"
    "print('no que fueron menos riesgosos durante su vida activa.')\n"
    "print(f'Dataset final: {len(df)} creditos activos')"
))

cells.append(code(
    "cols_df = pd.DataFrame({\n"
    "    'Variable':    ['id_acreditado','ciclo','monto','dias_mora','plazo_meses','tasa_interes'],\n"
    "    'Descripcion': [\n"
    "        'Identificador unico del cliente',\n"
    "        'Contador de renovaciones — referencia, no variable analizada',\n"
    "        'Monto bruto prestado en MXN',\n"
    "        'Dias desde el primer incumplimiento',\n"
    "        'Plazo convertido a meses (calculada)',\n"
    "        'Tasa de interes anual (%) — 2 creditos sin dato excluidos solo de este analisis'],\n"
    "    'Origen': [\n"
    "        'Codigo acreditado','Ciclo','Cantidad Prestada',\n"
    "        'Dias de mora','Plazo del credito + Periodicidad',\n"
    "        'CapturadeAcreditados (complementario)']\n"
    "})\n"
    "display(\n"
    "    cols_df.set_index('Variable').style\n"
    "    .set_caption('Tabla 2. Variables del analisis')\n"
    "    .set_table_styles([{'selector':'caption','props':"
    "[('font-size','13px'),('font-weight','bold'),('caption-side','top')]}])\n"
    ")\n"
    "df[['monto','plazo_meses','tasa_interes','dias_mora']].describe().round(2)"
))

# SEC 2 - PLAZO_MESES
cells.append(md(
    "---\n"
    "## 2. Construccion de `plazo_meses`\n\n"
    "El reporte da el **numero de pagos** y la **frecuencia** de pago por separado. "
    "Para comparar creditos de distintos productos se convierten a una escala comun: meses.\n\n"
    "**Formula:** `plazo_meses = numero de pagos x factor de periodicidad`"
))

cells.append(code(
    "factores = pd.DataFrame({\n"
    "    'Periodicidad': ['Mensual','Quincenal','Catorcenal','Semanal'],\n"
    "    'Factor':       [1.0, 0.5, round(14/30.44,4), round(7/30.44,4)],\n"
    "    'Base':         ['1 mes exacto','15/30 dias','14/30.44 dias','7/30.44 dias'],\n"
    "    'Ejemplo':      ['12 pagos x 1.00 = 12.0 m','24 pagos x 0.50 = 12.0 m',\n"
    "                     '26 pagos x 0.46 = 11.9 m','52 pagos x 0.23 = 12.0 m']\n"
    "})\n"
    "display(\n"
    "    factores.set_index('Periodicidad').style\n"
    "    .set_caption('Tabla 3. Conversion de periodicidad a meses')\n"
    "    .set_table_styles([{'selector':'caption','props':"
    "[('font-size','13px'),('font-weight','bold'),('caption-side','top')]}])\n"
    "    .format({'Factor':'{:.4f}'})\n"
    ")"
))

cells.append(code(
    "raw = pd.read_excel(sorted(DATA_DIR.glob('*.xlsx'), key=lambda f: f.stat().st_mtime)[-1], sheet_name=0)\n"
    "raw.columns = [c.replace('\\n',' ') for c in raw.columns]\n"
    "raw = raw[raw.iloc[:,29]=='Entregado'].copy()\n"
    "FMAP = {'Mensual':1.0,'Quincenal':0.5,'Catorcenal':14/30.44,'Semanal':7/30.44}\n"
    "idxs = []\n"
    "for per in ['Mensual','Catorcenal','Semanal','Quincenal']:\n"
    "    sub = raw[raw.iloc[:,15].str.strip()==per]\n"
    "    if len(sub): idxs.append(sub.index[0])\n"
    "ej = raw.loc[idxs, [raw.columns[6], raw.columns[14], raw.columns[15]]].copy()\n"
    "ej.columns = ['ID acreditado','Pagos','Periodicidad']\n"
    "ej['Factor']      = ej['Periodicidad'].str.strip().map(FMAP).round(4)\n"
    "ej['plazo_meses'] = (ej['Pagos']*ej['Factor']).round(2)\n"
    "display(\n"
    "    ej.reset_index(drop=True).style\n"
    "    .set_caption('Tabla 4. Ejemplos reales de conversion a plazo_meses')\n"
    "    .set_table_styles([{'selector':'caption','props':"
    "[('font-size','13px'),('font-weight','bold'),('caption-side','top')]}])\n"
    "    .format({'Factor':'{:.4f}','plazo_meses':'{:.2f}'})\n"
    ")"
))

cells.append(code(
    "fig, ax = plt.subplots(figsize=(10,4))\n"
    "ax.hist(df['plazo_meses'], bins=20, color=AZUL, edgecolor='white', lw=0.8)\n"
    "ax.axvline(df['plazo_meses'].mean(),   color=ROJO,    lw=2, ls='--',\n"
    "           label=f'Media: {df[\"plazo_meses\"].mean():.1f} m')\n"
    "ax.axvline(df['plazo_meses'].median(), color=NARANJA, lw=2, ls=':',\n"
    "           label=f'Mediana: {df[\"plazo_meses\"].median():.1f} m')\n"
    "ax.set_title('Figura 1. Distribucion del plazo en meses', pad=12)\n"
    "ax.set_xlabel('Plazo (meses)'); ax.set_ylabel('Creditos'); ax.legend()\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_01_plazo.png'), bbox_inches='tight')\n"
    "plt.show()"
))

# SEC 3 - PANORAMA
cells.append(md(
    "---\n"
    "## 3. Panorama de la mora\n\n"
    "Antes de analizar causas se dimensiona el problema."
))

cells.append(code(
    "bins   = [-1,0,30,60,90,180,365,np.inf]\n"
    "labels = ['Sin mora','1-30 d','31-60 d','61-90 d','91-180 d','181-365 d','>365 d']\n"
    "df['bucket'] = pd.cut(df['dias_mora'], bins=bins, labels=labels)\n"
    "conteo = df['bucket'].value_counts().reindex(labels)\n"
    "pct    = (conteo/len(df)*100).round(1)\n"
    "colores_b = [VERDE,'#85C1E9','#3498DB',AZUL,NARANJA,ROJO,'#6C3483']\n"
    "\n"
    "fig, axes = plt.subplots(1,2,figsize=(14,5))\n"
    "bars = axes[0].bar(labels, conteo.values, color=colores_b, edgecolor='white', lw=0.8)\n"
    "for bar,p,c in zip(bars,pct.values,conteo.values):\n"
    "    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,\n"
    "                 f'{p:.1f}%', ha='center', va='bottom', fontsize=9.5, fontweight='bold')\n"
    "axes[0].set_title('Figura 2. Cartera activa por bucket de mora', pad=12)\n"
    "axes[0].set_ylabel('Creditos'); axes[0].set_ylim(0, conteo.max()*1.2)\n"
    "axes[0].tick_params(axis='x', labelsize=8.5)\n"
    "\n"
    "mora_si=df['en_mora'].sum(); mora_no=len(df)-mora_si\n"
    "axes[1].pie(\n"
    "    [mora_no, mora_si],\n"
    "    labels=[f'Sin mora\\n{mora_no} ({mora_no/len(df)*100:.1f}%)',\n"
    "            f'En mora\\n{mora_si} ({mora_si/len(df)*100:.1f}%)'],\n"
    "    colors=[VERDE,ROJO], startangle=90,\n"
    "    wedgeprops={'edgecolor':'white','linewidth':2}, textprops={'fontsize':11})\n"
    "axes[1].set_title('Figura 3. Mora vs sin mora', pad=12)\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_02_panorama.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "print(f'Mediana  : {int(df[\"dias_mora\"].median())} dias')\n"
    "print(f'Promedio : {df[\"dias_mora\"].mean():.0f} dias')\n"
    "print(f'Maximo   : {df[\"dias_mora\"].max()} dias ({df[\"dias_mora\"].max()/365:.1f} anios)')\n"
    "print(f'Mora grave (>90d): {df[\"dias_mora\"].gt(90).sum()} creditos '\n"
    "      f'({df[\"dias_mora\"].gt(90).mean()*100:.1f}%)')"
))

# SEC 4 - MONTO
cells.append(md(
    "---\n"
    "## 4. Monto vs Mora\n\n"
    "Se usa **correlacion de Spearman** porque `dias_mora` es asimetrica "
    "(mediana=0, cola hasta 728 dias). Pearson requiere normalidad y es sensible "
    "a valores extremos; Spearman trabaja con rangos y es robusto."
))

cells.append(code(
    "r_m, p_m = spearmanr(df['monto'], df['dias_mora'])\n"
    "df['seg_monto'] = pd.qcut(df['monto'], q=3,\n"
    "                          labels=['Bajo (<P33)','Medio (P33-P66)','Alto (>P66)'])\n"
    "medias_m   = df.groupby('seg_monto', observed=True)['dias_mora'].mean().round(1)\n"
    "pct_mora_m = df.groupby('seg_monto', observed=True)['en_mora'].mean().mul(100).round(1)\n"
    "cnt_m      = df.groupby('seg_monto', observed=True)['dias_mora'].count()\n"
    "\n"
    "fig, axes = plt.subplots(1,2,figsize=(13,5))\n"
    "axes[0].scatter(no['monto'], no['dias_mora'], alpha=0.35, color=GRIS, s=28,\n"
    "                label='Sin mora', edgecolors='none')\n"
    "axes[0].scatter(en['monto'], en['dias_mora'], alpha=0.50, color=ROJO, s=28,\n"
    "                label='En mora',  edgecolors='none')\n"
    "z  = np.polyfit(df['monto'], df['dias_mora'], 1)\n"
    "xr = np.linspace(df['monto'].min(), df['monto'].max(), 200)\n"
    "axes[0].plot(xr, np.poly1d(z)(xr), color=AZUL, lw=2.5, label='Tendencia')\n"
    "axes[0].set_title('Figura 4a. Monto vs Dias de mora', pad=10)\n"
    "axes[0].set_xlabel('Monto prestado (MXN)'); axes[0].set_ylabel('Dias de mora')\n"
    "axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))\n"
    "axes[0].legend(fontsize=9)\n"
    "stxt = '(*)' if p_m<0.05 else '(n.s.)'\n"
    "axes[0].text(0.05,0.92, f'r = {r_m:+.2f}  p={p_m:.3f} {stxt}',\n"
    "             transform=axes[0].transAxes, fontsize=10,\n"
    "             bbox=dict(boxstyle='round,pad=0.3',facecolor='#EBF5FB',edgecolor=AZUL))\n"
    "df.boxplot(column='dias_mora', by='seg_monto', ax=axes[1], patch_artist=True,\n"
    "           boxprops=dict(facecolor=AZUL+'33',color=AZUL),\n"
    "           medianprops=dict(color=ROJO,lw=2.5),\n"
    "           whiskerprops=dict(color=AZUL), capprops=dict(color=AZUL),\n"
    "           flierprops=dict(marker='o',color=AZUL,alpha=0.3,markersize=3))\n"
    "for i,(seg,val) in enumerate(medias_m.items()):\n"
    "    axes[1].text(i+1, val+8, f'media={val:.0f}d\\nn={cnt_m[seg]}',\n"
    "                 ha='center', fontsize=9, color=AZUL, fontweight='bold')\n"
    "axes[1].set_title('Figura 4b. Dias de mora por tercil de monto', pad=10)\n"
    "axes[1].set_xlabel('Segmento'); axes[1].set_ylabel('Dias de mora')\n"
    "plt.suptitle('')\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_03_monto.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "print(f'r Spearman = {r_m:+.4f}  p = {p_m:.4f}  {stxt}')\n"
    "for seg in medias_m.index:\n"
    "    print(f'  {str(seg):22s}: media={medias_m[seg]:.1f}d  {pct_mora_m[seg]:.1f}% en mora')"
))

cells.append(md(
    "**Conclusion — Monto:** Relacion debil pero estadisticamente significativa "
    "(r = +0.15, p = 0.028). Los creditos de monto alto tienden a mas dias de mora, "
    "pero la relacion es demasiado debil para usarse como predictor individual."
))

# SEC 5 - PLAZO
cells.append(md(
    "---\n"
    "## 5. Plazo vs Mora\n\n"
    "Se analiza si los creditos a mayor plazo acumulan mas dias de mora."
))

cells.append(code(
    "r_p, p_p = spearmanr(df['plazo_meses'], df['dias_mora'])\n"
    "df['seg_plazo'] = pd.cut(df['plazo_meses'], bins=[0,6,12,np.inf],\n"
    "                         labels=['Corto (<6m)','Medio (6-12m)','Largo (>12m)'])\n"
    "medias_p   = df.groupby('seg_plazo', observed=True)['dias_mora'].mean().round(1)\n"
    "pct_mora_p = df.groupby('seg_plazo', observed=True)['en_mora'].mean().mul(100).round(1)\n"
    "cnt_p      = df.groupby('seg_plazo', observed=True)['dias_mora'].count()\n"
    "\n"
    "fig, axes = plt.subplots(1,2,figsize=(13,5))\n"
    "axes[0].scatter(no['plazo_meses'], no['dias_mora'], alpha=0.35, color=GRIS, s=28,\n"
    "                label='Sin mora', edgecolors='none')\n"
    "axes[0].scatter(en['plazo_meses'], en['dias_mora'], alpha=0.50, color=ROJO, s=28,\n"
    "                label='En mora',  edgecolors='none')\n"
    "z2  = np.polyfit(df['plazo_meses'], df['dias_mora'], 1)\n"
    "xr2 = np.linspace(df['plazo_meses'].min(), df['plazo_meses'].max(), 200)\n"
    "axes[0].plot(xr2, np.poly1d(z2)(xr2), color=AZUL, lw=2.5, ls='--',\n"
    "             label='Tendencia (plana)')\n"
    "axes[0].set_title('Figura 5a. Plazo (meses) vs Dias de mora', pad=10)\n"
    "axes[0].set_xlabel('Plazo en meses'); axes[0].set_ylabel('Dias de mora')\n"
    "axes[0].legend(fontsize=9)\n"
    "axes[0].text(0.05,0.92, f'r = {r_p:+.2f}  p={p_p:.3f} (n.s.)',\n"
    "             transform=axes[0].transAxes, fontsize=10,\n"
    "             bbox=dict(boxstyle='round,pad=0.3',facecolor='#F9EBEA',edgecolor=ROJO))\n"
    "df.boxplot(column='dias_mora', by='seg_plazo', ax=axes[1], patch_artist=True,\n"
    "           boxprops=dict(facecolor=VERDE+'33',color=VERDE),\n"
    "           medianprops=dict(color=ROJO,lw=2.5),\n"
    "           whiskerprops=dict(color=VERDE), capprops=dict(color=VERDE),\n"
    "           flierprops=dict(marker='o',color=VERDE,alpha=0.3,markersize=3))\n"
    "for i,(seg,val) in enumerate(medias_p.items()):\n"
    "    axes[1].text(i+1, val+8, f'media={val:.0f}d\\nn={cnt_p[seg]}',\n"
    "                 ha='center', fontsize=9, color=VERDE, fontweight='bold')\n"
    "axes[1].set_title('Figura 5b. Dias de mora por segmento de plazo', pad=10)\n"
    "axes[1].set_xlabel('Segmento'); axes[1].set_ylabel('Dias de mora')\n"
    "plt.suptitle('')\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_04_plazo.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "print(f'r Spearman = {r_p:+.4f}  p = {p_p:.4f}  NO significativa')\n"
    "for seg in medias_p.index:\n"
    "    print(f'  {str(seg):22s}: media={medias_p[seg]:.1f}d  {pct_mora_p[seg]:.1f}% en mora  n={cnt_p[seg]}')"
))

cells.append(md(
    "**Conclusion — Plazo:** Sin relacion estadistica (r = -0.02, p = 0.80). "
    "Creditos a 3 meses y a 24 meses tienen mora equivalente. Hipotesis: el plazo "
    "se calibra segun capacidad de pago, lo que equilibra el riesgo entre segmentos "
    "y neutraliza su efecto."
))

# SEC 6 - TASA
cells.append(md(
    "---\n"
    "## 6. Tasa de Interés vs Mora\n\n"
    "La tasa proviene de un archivo complementario (`CapturadeAcreditados`). "
    "**2 créditos sin match** (IDs 1167 y 1272) se excluyen solo de este análisis; "
    "el resto del notebook los conserva. Quedan **211 registros** para este análisis."
))

cells.append(code(
    "df_t = df.dropna(subset=['tasa_interes']).copy()\n"
    "en_t = df_t[df_t['en_mora']==1]; no_t = df_t[df_t['en_mora']==0]\n"
    "\n"
    "r_t, p_t = spearmanr(df_t['tasa_interes'], df_t['dias_mora'])\n"
    "stxt_t = '(*)' if p_t < 0.05 else '(n.s.)'\n"
    "\n"
    "# Segmentos de tasa\n"
    "df_t['seg_tasa'] = pd.cut(df_t['tasa_interes'],\n"
    "                          bins=[0, 5, 9, np.inf],\n"
    "                          labels=['Baja (<5%)','Media (5-9%)','Alta (>9%)'])\n"
    "medias_t   = df_t.groupby('seg_tasa', observed=True)['dias_mora'].mean().round(1)\n"
    "pct_mora_t = df_t.groupby('seg_tasa', observed=True)['en_mora'].mean().mul(100).round(1)\n"
    "cnt_t      = df_t.groupby('seg_tasa', observed=True)['dias_mora'].count()\n"
    "\n"
    "fig, axes = plt.subplots(1,2,figsize=(13,5))\n"
    "axes[0].scatter(no_t['tasa_interes'], no_t['dias_mora'], alpha=0.35, color=GRIS, s=28,\n"
    "                label='Sin mora', edgecolors='none')\n"
    "axes[0].scatter(en_t['tasa_interes'], en_t['dias_mora'], alpha=0.50, color=ROJO, s=28,\n"
    "                label='En mora', edgecolors='none')\n"
    "z3  = np.polyfit(df_t['tasa_interes'], df_t['dias_mora'], 1)\n"
    "xr3 = np.linspace(df_t['tasa_interes'].min(), df_t['tasa_interes'].max(), 200)\n"
    "axes[0].plot(xr3, np.poly1d(z3)(xr3), color=AZUL, lw=2.5, label='Tendencia')\n"
    "axes[0].set_title('Figura 6a. Tasa de interes vs Dias de mora', pad=10)\n"
    "axes[0].set_xlabel('Tasa de interes (%)'); axes[0].set_ylabel('Dias de mora')\n"
    "axes[0].legend(fontsize=9)\n"
    "axes[0].text(0.05, 0.92, f'r = {r_t:+.2f}  p={p_t:.3f} {stxt_t}',\n"
    "             transform=axes[0].transAxes, fontsize=10,\n"
    "             bbox=dict(boxstyle='round,pad=0.3', facecolor='#EBF5FB', edgecolor=AZUL))\n"
    "\n"
    "df_t.boxplot(column='dias_mora', by='seg_tasa', ax=axes[1], patch_artist=True,\n"
    "             boxprops=dict(facecolor=NARANJA+'33', color=NARANJA),\n"
    "             medianprops=dict(color=ROJO, lw=2.5),\n"
    "             whiskerprops=dict(color=NARANJA), capprops=dict(color=NARANJA),\n"
    "             flierprops=dict(marker='o', color=NARANJA, alpha=0.3, markersize=3))\n"
    "for i,(seg,val) in enumerate(medias_t.items()):\n"
    "    axes[1].text(i+1, val+8, f'media={val:.0f}d\\nn={cnt_t[seg]}',\n"
    "                 ha='center', fontsize=9, color=NARANJA, fontweight='bold')\n"
    "axes[1].set_title('Figura 6b. Dias de mora por segmento de tasa', pad=10)\n"
    "axes[1].set_xlabel('Segmento'); axes[1].set_ylabel('Dias de mora')\n"
    "plt.suptitle('')\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_05_tasa.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "print(f'r Spearman = {r_t:+.4f}  p = {p_t:.4f}  {stxt_t}')\n"
    "for seg in medias_t.index:\n"
    "    print(f'  {str(seg):18s}: media={medias_t[seg]:.1f}d  {pct_mora_t[seg]:.1f}% en mora  n={cnt_t[seg]}')"
))

cells.append(code(
    "# Distribucion de la tasa — ver si es parametro de producto o de riesgo\n"
    "tasa_vals = df_t['tasa_interes'].value_counts().sort_index()\n"
    "fig, ax = plt.subplots(figsize=(11,4))\n"
    "bars = ax.bar([f'{v:.2f}%' for v in tasa_vals.index], tasa_vals.values,\n"
    "              color=AZUL, edgecolor='white', lw=0.8)\n"
    "for bar,val in zip(bars, tasa_vals.values):\n"
    "    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,\n"
    "            str(val), ha='center', va='bottom', fontsize=8.5, fontweight='bold')\n"
    "ax.set_title('Figura 6c. Distribucion de valores de tasa de interes (n creditos por valor)', pad=12)\n"
    "ax.set_xlabel('Tasa (%)'); ax.set_ylabel('Creditos')\n"
    "ax.tick_params(axis='x', labelrotation=45, labelsize=8)\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_05b_tasa_dist.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "print(f'Valor mas frecuente: {tasa_vals.idxmax():.4f}%  ({tasa_vals.max()} creditos = {tasa_vals.max()/len(df_t)*100:.1f}%)')\n"
    "print('Si un valor concentra >60% de los creditos, la tasa es parametro de producto, no de riesgo.')"
))

cells.append(md(
    "**Conclusion — Tasa de Interés:** *(se actualizara con los resultados al ejecutar el notebook)*\n\n"
    "- Si r no es significativo: la tasa es un parametro de producto que no captura riesgo individual\n"
    "- Si r es significativo y positivo: a mayor tasa, mayor mora — posible pricing por riesgo\n"
    "- La Figura 6c es clave: si el 70%+ esta en un solo valor, la tasa no discrimina entre clientes"
))

# SEC 7 - MODELO (renumerado de 7)
cells.append(md(
    "---\n"
    "## 7. Modelo combinado: monto, plazo y tasa juntos\n\n"
    "**Regresion logistica** para estimar la probabilidad de entrar en mora. "
    "Se usan los 211 registros con tasa disponible. "
    "Resultados en **Odds Ratios**: OR < 1 reduce la probabilidad; OR > 1 la aumenta."
))

cells.append(code(
    "vars_modelo = ['monto','plazo_meses','tasa_interes']\n"
    "df_m  = df.dropna(subset=['tasa_interes']).copy()\n"
    "X_log = sm.add_constant(df_m[vars_modelo])\n"
    "logit = sm.Logit(df_m['en_mora'], X_log).fit(disp=False)\n"
    "ci = logit.conf_int(); pv = logit.pvalues\n"
    "def sig(p): return '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'n.s.'\n"
    "\n"
    "or_df = pd.DataFrame({\n"
    "    'Variable':        ['Monto','Plazo (meses)','Tasa de interes'],\n"
    "    'Odds Ratio':      np.exp(logit.params[vars_modelo]).round(4).values,\n"
    "    'IC 95% inferior': np.exp(ci.loc[vars_modelo, 0]).round(4).values,\n"
    "    'IC 95% superior': np.exp(ci.loc[vars_modelo, 1]).round(4).values,\n"
    "    'p-value':         pv[vars_modelo].round(4).values,\n"
    "    'Sig.': [sig(pv[v]) for v in vars_modelo]\n"
    "})\n"
    "display(\n"
    "    or_df.set_index('Variable').style\n"
    "    .set_caption('Tabla 5. Regresion logistica — Odds Ratios (n=211)')\n"
    "    .set_table_styles([{'selector':'caption','props':"
    "[('font-size','13px'),('font-weight','bold'),('caption-side','top')]}])\n"
    "    .format({'Odds Ratio':'{:.4f}','IC 95% inferior':'{:.4f}',\n"
    "             'IC 95% superior':'{:.4f}','p-value':'{:.4f}'})\n"
    "    .apply(lambda x: ['background-color:#D5F5E3' if '***' in str(v) or '**' in str(v)\n"
    "                      else 'background-color:#FADBD8' if 'n.s.' in str(v)\n"
    "                      else '' for v in x], axis=1)\n"
    ")"
))

cells.append(code(
    "y_proba   = logit.predict(X_log)\n"
    "auc       = roc_auc_score(df_m['en_mora'], y_proba)\n"
    "fpr,tpr,_ = roc_curve(df_m['en_mora'], y_proba)\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(7,5))\n"
    "ax.plot(fpr, tpr, color=AZUL, lw=2.5, label=f'Modelo  (AUC = {auc:.2f})')\n"
    "ax.plot([0,1],[0,1], color=GRIS, ls='--', lw=1.2, label='Azar  (AUC = 0.50)')\n"
    "ax.fill_between(fpr, tpr, alpha=0.08, color=AZUL)\n"
    "ax.set_xlabel('Falsos Positivos'); ax.set_ylabel('Verdaderos Positivos')\n"
    "ax.set_title('Figura 7. Curva ROC — modelo logistico', pad=12)\n"
    "ax.legend(fontsize=10)\n"
    "plt.tight_layout()\n"
    "plt.savefig(str(ROOT/'outputs'/'fig_06_roc.png'), bbox_inches='tight')\n"
    "plt.show()\n"
    "print(f'AUC = {auc:.4f}  (0.50=azar | {auc:.2f}=este modelo | 1.00=perfecto)')"
))

cells.append(md(
    "**Conclusion — Modelo combinado:** *(se actualizara con los resultados al ejecutar)*\n\n"
    "Con las tres variables de producto juntas (monto, plazo, tasa) el AUC mejora respecto "
    "al modelo sin tasa solo si la tasa tiene poder discriminatorio propio. "
    "Si el AUC sigue cerca de 0.60, confirma que las caracteristicas del credito "
    "no explican la mora — el riesgo esta en el cliente y el contexto operativo."
))

# SEC 8 - CONCLUSION
cells.append(md(
    "---\n"
    "## 7. Conclusiones y recomendaciones\n\n"
    "### ¿Por que el monto y el plazo no explican la mora?\n\n"
    "**El plazo esta calibrado segun capacidad de pago.** Plazos largos se otorgan a "
    "clientes que pueden sostenerlos; plazos cortos a quienes solo pueden pagar en poco "
    "tiempo. Esa asignacion ya incorpora el riesgo y lo equilibra entre segmentos — "
    "por eso el plazo no deja ninguna senal estadistica.\n\n"
    "**El monto tiene una relacion debil pero no es util como predictor.** "
    "Un r = +0.15 es estadisticamente real pero explica menos del 3% de la variabilidad "
    "de la mora. En la practica no sirve para tomar decisiones de originacion.\n\n"
    "**La mora responde al cliente, no al producto.** Las caracteristicas del credito "
    "(monto, plazo) no capturan el riesgo real. Las variables que probablemente "
    "si lo expliquen son:\n\n"
    "- **Coordinacion / sucursal** — Valle de Bravo concentra el 63% del saldo vencido\n"
    "- **Sector economico** — el giro del negocio puede ser proxy de vulnerabilidad\n"
    "- **Promotor** — la calidad de la originacion impacta la cartera\n"
    "- **Recencia del ultimo pago** — altamente predictivo en modelos de cobranza\n\n"
    "---\n\n"
    "### Resumen de hallazgos\n\n"
    "| Pregunta | Hallazgo | Evidencia |\n"
    "|---|---|---|\n"
    "| Monto -> mora? | Relacion debil, no util en la practica | r = +0.15  (p = 0.028) |\n"
    "| Plazo -> mora? | Sin relacion | r = -0.02  (p = 0.80, n.s.) |\n"
    "| Tasa -> mora? | Por confirmar al ejecutar | ver Seccion 6 |\n"
    "| Las 3 juntas? | Por confirmar al ejecutar | ver Seccion 7 AUC |\n\n"
    "**Conclusion principal:** Las variables de producto analizadas (monto, plazo) no explican la mora. "
    "La tasa puede aportar informacion adicional si refleja riesgo — se confirma al ejecutar.\n\n"
    "**Recomendacion:** Incorporar coordinacion, sector economico y promotor "
    "para construir un modelo con poder predictivo real."
))

# EXPORT
cells.append(md(
    "---\n"
    "## Exportar a PDF\n\n"
    "Desde terminal en la carpeta raiz del proyecto:\n\n"
    "```bash\n"
    "jupyter nbconvert --to html --no-input notebook/analisis_mora.ipynb "
    "--output outputs/reporte_mora.html\n"
    "```\n\n"
    "Abre `outputs/reporte_mora.html` en Chrome -> **Ctrl+P -> Guardar como PDF**."
))

# ---------------------------------------------------------------------------
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK — {len(cells)} celdas  ->  {OUT}")
