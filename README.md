# Guía de presentación — Análisis de Mora Crediticia

> Esto es tu cheat sheet. Cubre cada sección del notebook, qué dice cada gráfica, los conceptos estadísticos en lenguaje simple y las preguntas que te pueden hacer.

---

## Contexto general (di esto para abrir)

> *"Analizamos 213 créditos activos de la cartera Estado México al 6 de marzo. La pregunta era simple: ¿el monto, el plazo o la tasa del crédito explican si un cliente cae en mora? El resultado más importante es que la tasa sí lo predice — y con fuerza."*

---

## Sección 1 — Origen y preparación de los datos

**Qué hay aquí:** Una tabla que muestra cuántos registros entraron al análisis y cuántos se descartaron.

| Situación | Registros | ¿Por qué? |
|---|---|---|
| Entregado (activos) | 213 | **Estos son los que analizamos** |
| Liquidado | 133 | Ya pagaron — su mora=0 no refleja riesgo |
| Autorizado por cartera | 1 | Caso aislado |

**Qué decir:**
> *"Solo trabajamos con créditos activos. Los liquidados los excluimos porque ya terminaron de pagar — si los metiéramos, inflarían el grupo 'sin mora' con ceros que no significan nada para predecir riesgo futuro."*

**Pregunta frecuente:** *¿Por qué no analizas los liquidados?*
> Porque nos interesa saber qué características tiene un crédito que **está** fallando, no uno que ya cerró bien o mal. Mezclarlos distorsionaría el análisis.

---

## Sección 2 — Construcción de `plazo_meses`

**Qué hay aquí:** Explicación de cómo se convirtió el plazo a meses, porque el archivo original lo trae en número de pagos con distintas frecuencias.

**La fórmula:** `plazo_meses = número de pagos × factor`

| Periodicidad | Factor | Ejemplo |
|---|---|---|
| Mensual | 1.0 | 12 pagos × 1.0 = 12 meses |
| Quincenal | 0.5 | 24 pagos × 0.5 = 12 meses |
| Semanal | 0.23 | 52 pagos × 0.23 = 12 meses |

**Figura 1 — Histograma del plazo:**
- Eje X: cuántos meses dura el crédito
- Eje Y: cuántos créditos tienen ese plazo
- Las líneas verticales muestran la media y mediana

**Qué decir:**
> *"El plazo venía en pagos con distintas frecuencias, así que lo normalizamos a meses para poder comparar un crédito semanal contra uno mensual en la misma escala."*

---

## Sección 3 — Panorama de la mora

**Figura 2 — Barras de buckets de mora:**
Agrupa los créditos por cuántos días llevan en mora:
- `Sin mora`: 0 días (pagando bien)
- `1-30 d`: atraso reciente
- `>365 d`: mora grave, más de 1 año

**Figura 3 — Pay chart mora/sin mora:**
- Verde: sin mora
- Rojo: en mora

**Números clave que debes recordar:**
- **65.7% en mora** (140 de 213 créditos)
- **50.2% en mora grave** (>90 días)
- Mediana: 91 días | Promedio: 170 días | Máximo: 728 días (2 años)

**Qué decir:**
> *"Antes de buscar causas, dimensionamos el problema. Dos tercios de la cartera activa tiene algún día de mora. Uno de cada dos créditos lleva más de 90 días — eso ya es mora grave que impacta provisiones."*

**Pregunta frecuente:** *¿Por qué la mediana y el promedio son tan distintos?*
> Porque hay unos pocos créditos con mora muy alta (728 días) que jalan el promedio hacia arriba. La mediana es más representativa de la mayoría.

---

## Sección 4 — Monto vs Mora

**Figura 4a — Scatter monto vs días de mora:**
- Cada punto es un crédito
- Puntos grises: sin mora | Puntos rojos: en mora
- La línea azul es la tendencia (regresión lineal visual)
- El recuadro muestra `r` y `p`

**Figura 4b — Cajas por tercil de monto:**
- Divide los créditos en tercios: montos bajos, medios y altos
- Cada caja muestra cómo se distribuyen los días de mora en ese grupo
- La línea roja dentro de la caja = mediana

**Resultado:** r = +0.15, p = 0.028

**Qué decir:**
> *"Hay una relación débil pero real: montos más altos tienden a más mora. El r de +0.15 es estadísticamente significativo — no es azar — pero explica menos del 3% de la variabilidad. En la práctica, el monto solo no te dice si un cliente va a caer en mora."*

**Pregunta frecuente:** *¿Qué es r?*
> Es la correlación de Spearman — un número entre -1 y +1. Cero significa sin relación, 1 significa relación perfecta positiva. Un +0.15 es débil. Un +0.58 (como la tasa) es fuerte.

---

## Sección 5 — Plazo vs Mora

**Figuras 5a y 5b:** Igual que la sección anterior pero con el plazo en meses.

**Resultado:** r = -0.02, p = 0.80 — **SIN relación**

**Qué decir:**
> *"El plazo no explica nada. Un crédito a 3 meses y uno a 24 meses tienen la misma probabilidad de caer en mora. Esto tiene sentido: el plazo se asigna según la capacidad de pago del cliente, así que ya lleva incorporado el riesgo — y lo equilibra entre grupos."*

**Pregunta frecuente:** *¿Entonces para qué analizamos el plazo si no sirve?*
> Precisamente para poder decirlo con datos. Sin el análisis, alguien podría asumir que créditos a mayor plazo son más riesgosos. Aquí lo descartamos formalmente.

---

## Sección 6 — Tasa de Interés vs Mora

**De dónde viene la tasa:** De un archivo complementario `CapturadeAcreditados`. Se cruzó por ID de cliente. 2 créditos no tenían registro — se excluyen solo de esta sección.

**Figura 6a — Scatter tasa vs días de mora:**
- Igual al de monto pero en eje X va la tasa (%)
- Verás una tendencia mucho más clara que en monto o plazo

**Figura 6b — Cajas por segmento de tasa:**
| Segmento | % en mora | Media días mora |
|---|---|---|
| Baja (<5%) | 23.1% | 60 días |
| Media (5–9%) | 61.0% | 77 días |
| **Alta (>9%)** | **97.4%** | **593 días** |

**Figura 6c — Distribución de valores de tasa:**
- Muestra cuántos créditos tiene cada valor de tasa
- El 70% está en 7.18% — un solo valor
- Hay 25 créditos en 13.27% y son casi todos en mora

**Resultado:** r = +0.58, p < 0.001 — **Relación fuerte, muy significativa**

**Qué decir:**
> *"Este es el hallazgo principal. La tasa explica la mora mucho mejor que el monto o el plazo. Los créditos con tasa alta tienen 97% de mora y en promedio casi 2 años de atraso. La tasa no es arbitraria — refleja el segmento de riesgo del producto. Los productos de mayor tasa se colocaron en perfiles de mayor riesgo, y eso se ve claramente en los datos."*

**Pregunta frecuente:** *¿Pero si el 70% tiene la misma tasa (7.18%), cómo puede ser tan predictiva?*
> Porque el otro 30% se polariza: el grupo de tasa baja (<5%) casi no tiene mora, y el de tasa alta (>9%) tiene mora prácticamente universal. Esa separación es muy informativa aunque el grupo mayoritario sea homogéneo.

**Pregunta frecuente:** *¿La tasa alta causa la mora, o los clientes riesgosos reciben tasa alta?*
> Es la segunda. La tasa es asignada al momento de la originación según el perfil o producto. Lo que estamos viendo es que ese criterio de asignación captura bien el riesgo real. No es que la tasa cause mora — es que ambas son consecuencia del mismo perfil de cliente.

---

## Sección 7 — Modelo combinado (Regresión Logística)

**Qué es una regresión logística:**
> Es un modelo que calcula la probabilidad de que algo ocurra (en este caso, caer en mora) usando varias variables al mismo tiempo. A diferencia de la correlación que ve cada variable sola, aquí las tres compiten juntas.

**Tabla de Odds Ratios:**

| Variable | OR | p-value | Significado |
|---|---|---|---|
| Monto | 1.00 | 0.565 | Sin efecto cuando entra la tasa |
| Plazo | 0.94 | 0.234 | Sin efecto |
| **Tasa** | **1.74** | **<0.001** | **Único predictor real** |

**Qué es un Odds Ratio (OR):**
> OR = 1 significa sin efecto. OR > 1 aumenta la probabilidad de mora. OR = 1.74 significa que por cada punto porcentual adicional de tasa, la probabilidad de mora sube 74%. Es un efecto grande.

**Figura 7 — Curva ROC:**
- La línea diagonal gris es el azar puro (lanzar una moneda)
- La línea azul es el modelo
- Cuanto más hacia arriba-izquierda, mejor el modelo
- **AUC = 0.71** — el área bajo la curva

**Qué es el AUC:**
> AUC de 0.50 = el modelo no sirve para nada (azar). AUC de 1.0 = modelo perfecto. Nuestro 0.71 significa que si tomas un crédito en mora y uno sin mora al azar, el modelo los ordena correctamente el 71% de las veces. Es moderado-bueno para solo tres variables de producto.

**Qué decir:**
> *"Cuando metemos las tres variables juntas, el monto y el plazo pierden toda significancia. La tasa se lleva todo el poder predictivo. Esto confirma que lo que importa es el perfil de riesgo del producto, no las condiciones financieras específicas. El modelo acierta 71 de cada 100 veces — nada mal para tres variables, con margen de mejora."*

---

## Sección 8 — Conclusiones

**Resumen para decir en 30 segundos:**
> *"Monto y plazo no explican la mora. La tasa sí — y con fuerza. Los productos de tasa alta tienen mora casi universal. El siguiente paso es agregar coordinación, sector económico y promotor para superar AUC 0.80."*

**Tabla resumen:**

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿Monto → mora? | Señal débil, desaparece al controlar por tasa | r = +0.15 |
| ¿Plazo → mora? | Sin relación | r = -0.02 |
| ¿Tasa → mora? | Relación fuerte, predictor dominante | r = +0.58, OR = 1.74 |
| ¿Las 3 juntas? | AUC = 0.71, dominado por tasa | Modelo moderado-bueno |

---

## Conceptos estadísticos en lenguaje simple

### Correlación de Spearman
No mide si hay una línea recta entre dos variables (eso sería Pearson). Mide si cuando una sube, la otra también tiende a subir — sin importar si la relación es lineal. Se usa porque `dias_mora` está muy sesgada (la mayoría tiene pocos días, unos pocos tienen cientos). Spearman es robusto ante eso.

### p-value
La probabilidad de ver este resultado por puro azar si en realidad no hubiera relación. p < 0.05 = significativo (menos de 5% de probabilidad de que sea azar). p < 0.001 = muy significativo.

### Odds Ratio
Si OR = 1.74 para la tasa: por cada unidad que sube la tasa, las *odds* de estar en mora se multiplican por 1.74. En términos prácticos: más tasa = mucho más probable caer en mora.

### AUC-ROC
Mide qué tan bien el modelo separa "va a entrar en mora" de "no va a entrar". 0.50 = azar, 1.0 = perfecto. 0.71 = bueno para el contexto.

---

## Preguntas difíciles y cómo responderlas

**"¿Por qué no usas más variables?"**
> Este análisis se enfoca en las variables de producto (las que el área de crédito controla al otorgar). El siguiente paso natural es incorporar variables del cliente y operativas: coordinación, sector, promotor.

**"¿El modelo sirve para tomar decisiones de originación?"**
> Con AUC 0.71 tiene poder discriminatorio real, pero no es suficiente para usarlo solo. Sirve como una señal más dentro de un proceso de evaluación, no como criterio único.

**"¿Por qué hay tanta mora en esta cartera?"**
> El análisis describe la relación entre variables, no sus causas profundas. Lo que sí podemos decir es que los productos de mayor tasa concentran el riesgo — lo que sugiere que el criterio de asignación de tasas ya captura algo del perfil de riesgo del cliente.

**"¿Qué pasa con los 2 créditos sin tasa?"**
> Son IDs que no tenían registro en el archivo complementario. Se excluyen solo del análisis de tasa y del modelo — siguen en el panorama de mora y en los análisis de monto y plazo. Son 2 de 213, no cambian ninguna conclusión.

**"¿La correlación de la tasa no es obvia? Si te prestan caro es porque eres riesgoso."**
> Exacto — y eso valida el modelo. Lo que estamos confirmando es que el criterio de pricing usado al originación predice bien el comportamiento real. Eso es útil: significa que el proceso de asignación de tasas captura riesgo real, y que se puede usar como variable en un modelo de alerta temprana.

---

## Cómo correr el notebook

**Colab (recomendado):**
1. [colab.research.google.com](https://colab.research.google.com) → Archivo → Abrir notebook → GitHub
2. Pega: `uzzielvz/analisis-crediticos`
3. Selecciona `notebook/analisis_mora.ipynb`
4. `Ctrl+F9` — ejecuta todo automáticamente

**Local:**
```bash
git clone https://github.com/uzzielvz/analisis-crediticos.git
cd analisis-crediticos
pip install pandas openpyxl matplotlib scipy statsmodels scikit-learn jupyter
jupyter notebook notebook/analisis_mora.ipynb
```

---

## Celda corregida — Monto vs Mora (filtro $0–$30K)

Reemplaza el contenido completo de la celda de monto con esto:

```python
from scipy.stats import spearmanr

df_m30 = df[df['monto'] <= 30000].copy()
en_m30 = df_m30[df_m30['en_mora']==1]
no_m30 = df_m30[df_m30['en_mora']==0]

r_m, p_m = spearmanr(df_m30['monto'], df_m30['dias_mora'])
df_m30['seg_monto'] = pd.qcut(df_m30['monto'], q=3,
                          labels=['Bajo (<P33)','Medio (P33-P66)','Alto (>P66)'])
medias_m   = df_m30.groupby('seg_monto', observed=True)['dias_mora'].mean().round(1)
pct_mora_m = df_m30.groupby('seg_monto', observed=True)['en_mora'].mean().mul(100).round(1)
cnt_m      = df_m30.groupby('seg_monto', observed=True)['dias_mora'].count()

fig, axes = plt.subplots(1,2,figsize=(13,5))
axes[0].scatter(no_m30['monto'], no_m30['dias_mora'], alpha=0.35, color=GRIS, s=28,
                label='Sin mora', edgecolors='none')
axes[0].scatter(en_m30['monto'], en_m30['dias_mora'], alpha=0.50, color=ROJO, s=28,
                label='En mora',  edgecolors='none')
z  = np.polyfit(df_m30['monto'], df_m30['dias_mora'], 1)
xr = np.linspace(df_m30['monto'].min(), df_m30['monto'].max(), 200)
axes[0].plot(xr, np.poly1d(z)(xr), color=AZUL, lw=2.5, label='Tendencia')
axes[0].set_title('Figura 4a. Monto vs Dias de mora (hasta $30K)', pad=10)
axes[0].set_xlabel('Monto prestado (MXN)'); axes[0].set_ylabel('Dias de mora')
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))
axes[0].legend(fontsize=9)
stxt = '(*)' if p_m<0.05 else '(n.s.)'
axes[0].text(0.05,0.92, f'r = {r_m:+.2f}  p={p_m:.3f} {stxt}',
             transform=axes[0].transAxes, fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3',facecolor='#EBF5FB',edgecolor=AZUL))
df_m30.boxplot(column='dias_mora', by='seg_monto', ax=axes[1], patch_artist=True,
           boxprops=dict(facecolor=AZUL+'33',color=AZUL),
           medianprops=dict(color=ROJO,lw=2.5),
           whiskerprops=dict(color=AZUL), capprops=dict(color=AZUL),
           flierprops=dict(marker='o',color=AZUL,alpha=0.3,markersize=3))
for i,(seg,val) in enumerate(medias_m.items()):
    axes[1].text(i+1, val+8, f'media={val:.0f}d\nn={cnt_m[seg]}',
                 ha='center', fontsize=9, color=AZUL, fontweight='bold')
axes[1].set_title('Figura 4b. Dias de mora por tercil de monto ($0-$30K)', pad=10)
axes[1].set_xlabel('Segmento'); axes[1].set_ylabel('Dias de mora')
plt.suptitle('')
plt.tight_layout()
plt.show()
print(f'n = {len(df_m30)} creditos (monto <= $30K, excluidos {len(df)-len(df_m30)} outliers)')
print(f'r Spearman = {r_m:+.4f}  p = {p_m:.4f}  {stxt}')
for seg in medias_m.index:
    print(f'  {str(seg):22s}: media={medias_m[seg]:.1f}d  {pct_mora_m[seg]:.1f}% en mora')
```
