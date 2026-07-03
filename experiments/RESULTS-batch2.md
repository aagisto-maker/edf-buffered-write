# Resultados — Lote 2 (caracterización fina + figuras)

## Caracterización de EDFlib-Python (confirmada empíricamente)

El docstring de `EDFwriter.writeSamples` exige: *"Size of buf should be equal to
or bigger than the samplefrequency"* (≥ tamaño de record). Prueba directa:

| Bloque de entrada | Resultado |
|---|---|
| **record completo (1000)** | Fichero correcto, duración 10 s. **OK.** |
| **sub-record (100)** | **Fichero malformado**, falla al leer (OSError). |

**Conclusión de la comparación de tres implementaciones (independientes):**

| Librería | Diseño | Ante bloques sub-record |
|---|---|---|
| **pyedflib** (wrapper C de EDFlib) | incremental | **Rellena en silencio** → fichero válido pero corrupto (inflación 10×). **Peligroso: falla silencioso.** |
| **EDFlib-Python** (port en Python puro) | incremental | **Rompe el fichero** (no conforme, error al leer). Fallo ruidoso. |
| **edfio** (independiente) | fichero entero | **No tiene ruta incremental** → el pitfall no puede surgir; pero exige toda la grabación en memoria. |

**Mensaje central para el paper (honesto y más fuerte que la v1):** la misma API
conceptual, en tres implementaciones, se comporta de tres formas distintas ante
bloques sub-record. Solo pyedflib produce el fallo *silencioso*, que es
precisamente lo peligroso. No puedes fiarte del comportamiento de ninguna librería
concreta: hay que **alinear al tamaño de record en el llamante** (patrón
buffer-then-flush) y **verificar con un round-trip integrity test**.

## Figuras generadas

- `Fig_inflation_law.png` — la inflación medida (pyedflib) cae exactamente sobre la
  ley teórica record/bloque. Convierte "es una consecuencia esperable del padding"
  en un resultado cuantitativo propio.
- `Fig_PSD_contamination.png` — original y buffered se solapan; el naive atenúa el
  pico de 80 Hz ~50× y esparce energía por toda la banda (config base 1 kHz,
  bloque 100, record 1 s).

## Datos reales (HECHO)

Round-trip sobre **EMG real de emgteach** (`emg_2026-06-28_20-52.edf`, canal
"EMG 2", 1000 Hz, 58 s; señal muscular real). Script: `realdata_roundtrip.py`.

| Escritura | Duración | Inflación | RMS_ratio |
|---|---|---|---|
| **naive** (bloques sub-record) | 580 s | **10×** | 0,316 |
| **buffered** (fix) | 58 s | 1× | 1,000 |

Figura `Fig_realdata_PSD.png`: el espectro EMG real (banda ancha ~10–150 Hz con
pico de red a 50 Hz) se **preserva exacto** con buffered y se **hunde ~2 órdenes
de magnitud en toda la banda** con naive. Es la prueba sobre datos reales que
pedía el Revisor 2, y con datos del propio proyecto (elegante).

> Angel dejó **tres** EMG válidos en `realdata/` (43, 44 y 58 s, 2 canales cada uno,
> 1 kHz, mV); se usó el de 58 s por ser el más largo y con más actividad. Los otros
> dos sirven de réplica si se quiere robustez adicional.

---

## Estado del material experimental: COMPLETO

Ya tenemos todo lo que pedían los revisores: barrido multi-config (ley de
inflación), tres implementaciones independientes caracterizadas, y datos reales.
Siguiente paso: **reescribir el manuscrito** con el reencuadre (tarea 11).
