# Resultados — Lote 1 (harness multi-librería / multi-config)

> Script: `harness_multilibrary.py`. Ejecutado el 2026-07-02.
> pyedflib 0.1.42, edfio 0.4.13, EDFlib-Python, numpy 2.2.6, scipy 1.15.3.

## A) Tres implementaciones (config base: fs=1000 Hz, record=1 s, bloque=100, T=10 s, 1 canal)

| Implementación | Tipo de API | Duración | Inflación | RMS_ratio | %<1 LSB |
|---|---|---|---|---|---|
| **pyedflib** (wrapper C de EDFlib), naive incremental | incremental | 100 s | **10×** | 0,316 | 90,0 |
| pyedflib, **buffered** (nuestra solución) | incremental | 10 s | 1× | 1,000 | 0,1 |
| **EDFlib-Python** (port en Python puro), naive incremental | incremental | — | *(fichero no compliant)* | — | — |
| **edfio** (independiente), whole-file | fichero entero | 10 s | 1× | 1,000 | 0,0 |

**Lecturas clave (honestas y publicables):**

1. El fallo es una propiedad de la **API de escritura incremental**, no del formato EDF ni de "un bug de pyedflib". pyedflib lo exhibe porque ofrece esa ruta.
2. **edfio** (implementación independiente) escribe el **fichero entero** y por diseño **no tiene ruta incremental** → el pitfall no puede surgir. Pero exige tener toda la grabación en memoria: no sirve para streaming en tiempo real sin que el llamante bufferice todo.
3. **EDFlib-Python** (mismo diseño EDFlib, port puro) **no silencia el problema igual**: en la primera prueba, alimentado con bloques < record produjo un **fichero no conforme** (fallo duro al leer), en vez del padding silencioso de pyedflib. → Distintas implementaciones de la misma API **divergen** en cómo tratan bloques sub-record: pyedflib **rellena en silencio** (peligroso), EDFlib-Python **rompe el fichero**. Moraleja reforzada: no puedes fiarte de ninguna; **alinea tú al tamaño de record**. *(Pendiente: caracterizar con precisión el comportamiento de EDFlib-Python en el lote 2.)*

## B) Barrido de configuraciones en pyedflib (naive incremental)

La inflación sigue exactamente **fs·d / bloque**, y la atenuación de RMS ≈ **√(bloque / (fs·d))**.

| fs (Hz) | record (s) | bloque | nº canales | Inflación | RMS_ratio | %<1 LSB |
|---|---|---|---|---|---|---|
| 256 | 1,0 | 32 | 1 | 8× | 0,353 | 87,5 |
| 1000 | 1,0 | 100 | 1 | 10× | 0,316 | 90,0 |
| 1000 | 1,0 | 100 | **4** | 10× | 0,316 | 90,0 |
| 1000 | 0,1 | 10 | 1 | 10× | 0,316 | 90,0 |
| 1000 | 5,0 | 100 | 1 | 50× | 0,141 | 98,0 |
| 4000 | 1,0 | 200 | 1 | 20× | 0,224 | 95,0 |
| 1000 | 1,0 | 50 | 1 | 20× | 0,224 | 95,0 |
| 1000 | 1,0 | 250 | 1 | 4× | 0,500 | 75,0 |

**Lecturas:**

- El efecto es **determinista y predecible**: inflación = fs·d/bloque, RMS_ratio = √(bloque/(fs·d)), %<1 LSB = (1 − bloque/(fs·d))·100. Esto convierte el "es una consecuencia esperable del padding" (crítica de R2) en un **resultado cuantitativo propio**: damos la ley exacta de la degradación.
- **Multicanal (4 canales)** se comporta igual que 1 canal → el fallo no depende del nº de canales.
- Cubre varias **fs** (256, 1000, 4000), **duraciones de record** (0,1–5 s) y **tamaños de bloque** (10–250) → responde a "un solo escenario".

## Pendiente (lote 2)

1. Caracterizar con precisión **EDFlib-Python** (¿siempre rompe el fichero? ¿en qué condiciones?) y confirmar el comportamiento de **MNE** (usa EDFlib-Python en modo whole-file → no debería sufrirlo).
2. **Dataset EDF real** (PhysioNet Sleep-EDF): leer un EEG real, re-emitirlo en bloques sub-record por pyedflib, mostrar la corrupción sobre datos reales y la restauración con buffered.
3. Figuras nuevas (inflación vs bloque/record; PSD sobre datos reales).
