# edf-buffered-write

A buffer-then-flush EDF/EDF+ writer and a library-independent round-trip
integrity test that **prevent** and **detect** silent corruption of European
Data Format recordings during real-time biopotential streaming.

[![CI](https://github.com/aagisto-maker/edf-buffered-write/actions/workflows/ci.yml/badge.svg)](https://github.com/aagisto-maker/edf-buffered-write/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21163099.svg)](https://doi.org/10.5281/zenodo.21163099)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The DOI above is the *concept* DOI and always resolves to the latest version.

## The problem

Real-time acquisition hardware delivers short blocks (often 10–100 samples per
read), but an incremental EDF/EDF+ writer such as `pyedflib` commits **one full
data record per call**, padding the unused remainder. Handing each sub-record
device block straight to the writer therefore produces a structurally valid
EDF+ file that is silently **inflated in duration** by the factor `fs·d / b`,
**attenuated in RMS amplitude** by `√(b / fs·d)`, and **distorted in spectrum** —
and no error is raised, so the damage propagates undetected into downstream
analysis.

## What this package provides

1. **A reusable buffer-then-flush writer** (`edf_buffered_write.BufferedEdfWriter`)
   that wraps a `pyedflib.EdfWriter`, accepts blocks of any size, commits only
   complete records, and pads just the final record with the last acquired value
   (not zero). It is a drop-in fix local to the acquisition loop; readers and
   already-written files are unaffected.
2. **A library-independent round-trip integrity test** that writes a signal of
   known statistics, reads it back and compares reported duration, RMS amplitude
   and power spectral density, so the failure can be caught in a
   continuous-integration pipeline regardless of the writing library.

It also bundles the characterisation harness (configuration sweep and
three-writer comparison), the real-data round-trip, and two de-identified real
surface-EMG recordings, so every figure and number in the accompanying software
metapaper can be reproduced.

## Install

```bash
pip install -e .          # installs the edf_buffered_write library
```

## Usage

```python
import pyedflib
from edf_buffered_write import BufferedEdfWriter

writer = pyedflib.EdfWriter("out.edf", n_channels)
writer.setSignalHeaders(headers)          # your per-signal headers
writer.setDatarecordDuration(1.0)         # 1 s records

bw = BufferedEdfWriter(writer)
while acquiring:
    block = device.read(100)              # any block size is fine
    bw.write_samples([block])             # one array per signal
bw.close()                                # flushes and closes the writer
```

`write_samples` takes one array per signal; `close` flushes the remainder
(padding the final record with the last value) and closes the underlying writer.

## Contents

| Path | Purpose |
|---|---|
| `edf_buffered_write/` | The reusable library (`BufferedEdfWriter`). |
| `pyproject.toml` | Packaging metadata; makes the library `pip install`-able. |
| `test_buffered_writer.py` | `pytest` tests of the library API (no inflation, amplitude preserved, multichannel, input validation). |
| `test_roundtrip.py` | `pytest` round-trip integrity tests via the harness (naive corrupts, buffered preserves, inflation law holds across configs). |
| `.github/workflows/ci.yml` | Continuous integration on Python 3.10–3.12. |
| `harness_multilibrary.py` | Configuration sweep (Table 1) and three-implementation comparison (Table 2). Functions importable via a guarded `main()`. |
| `make_figures.py` | Regenerates the synthetic-signal characterisation figures (time-domain, inflation law, PSD contamination). |
| `make_pseudocode.py` | Regenerates the side-by-side pseudocode figure (shown inline as Listing 1 in the paper). |
| `realdata_roundtrip.py` | Round-trip of a real EDF recording through the naive and buffered patterns; produces the PSD figures. |
| `emgteach_real_sEMG_2ch_1kHz_58s.edf` | De-identified real surface-EMG recording, BITalino, 2 ch, 1 kHz, 58 s (manuscript **Figure 2**). |
| `emgteach_real_sEMG_MyoWare_1ch_1kHz_24s.edf` | De-identified real surface-EMG recording, MyoWare 2.0 + Arduino-compatible board, 1 ch, 1 kHz, 24 s (manuscript **Figure 3**). |
| `Fig_*.png` | Manuscript and characterisation figures (300 dpi). |
| `requirements.txt` | Pinned dependency versions. |
| `DATA_LICENSE.md` / `LICENSE-CC0-1.0.txt` | Data licence (CC0-1.0) for the de-identified `.edf` recordings, separate from the MIT-licensed code. |

Manuscript figure map: **Figure 1** = `Fig_timedomain_burst_padding.png`
(time-domain bursts + padding vs. continuous signal); **Figure 2** =
`Fig_realdata_PSD.png` (BITalino recording); **Figure 3** =
`Fig_realdata_PSD_MyoWare.png` (MyoWare recording). `Fig_inflation_law.png` and
`Fig_PSD_contamination.png` are additional synthetic-characterisation figures.

## Requirements

Python ≥ 3.10. The library itself needs only `numpy` and `pyedflib`; the harness,
figures and cross-implementation comparison additionally use `scipy`,
`matplotlib`, `EDFlib-Python` and `edfio`.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Reproduce

```bash
# Table 1 (configuration sweep) + Table 2 (three implementations)
python harness_multilibrary.py

# Synthetic-signal characterisation figures
python make_figures.py

# Real-data round-trip, using an included de-identified recording
python realdata_roundtrip.py emgteach_real_sEMG_2ch_1kHz_58s.edf 1 100
python realdata_roundtrip.py emgteach_real_sEMG_MyoWare_1ch_1kHz_24s.edf 1 100
```

## Testing

```bash
pip install -e . pytest
pytest -v
```

`test_buffered_writer.py` exercises the shipped `BufferedEdfWriter` API;
`test_roundtrip.py` asserts that the naive per-block writer corrupts the
recording (duration inflated by `fs·d/b`, RMS attenuated by its square root),
that the buffer-then-flush writer preserves duration and amplitude, and that the
deterministic inflation law holds across a range of sampling rates, record
durations and block sizes. The same tests run in continuous integration on
Python 3.10–3.12 (`.github/workflows/ci.yml`).

All synthetic results use a fixed random seed (42), so the numbers are
reproducible across machines. Base configuration (fs = 1 kHz, 1 s records,
100-sample blocks):

| Quantity                                      | Naive | Buffered |
|-----------------------------------------------|-------|----------|
| Reported file duration (s)                    | 100.0 | 10.0     |
| Read-back RMS amplitude (mV)                  | 0.069 | 0.218    |
| Samples within ±1 LSB of zero (%)             | 90.0  | 0.1      |
| PSD attenuation factor at 80 Hz (vs original) | ×51   | ×1.0     |

## Real surface-EMG recordings

Both recordings are **de-identified** EDF+ files (all patient header sub-fields
are `X`, unknown) and are the author's own signals, recorded from himself during
software development:

- `emgteach_real_sEMG_2ch_1kHz_58s.edf` — BITalino board, 2 channels, 1 kHz,
  58 s, physical units mV.
- `emgteach_real_sEMG_MyoWare_1ch_1kHz_24s.edf` — Arduino-compatible board with a
  MyoWare 2.0 sensor, 1 channel, 1 kHz, 24 s, physical units mV.

## Power spectral density protocol

Welch's method on each read-back signal (1024-sample segments, 50 % overlap,
physical units mV). The attenuation factor is the ratio of PSD between the
original in-memory signal and the naive file in the EMG band.

## Upstream contribution

The buffered writer has also been proposed upstream to `pyedflib` (issue #284 and
pull request #285), which adds an opt-in buffered writer to the library itself,
so downstream projects may inherit the fix directly.

## How to cite

- Agis-Torres, Á. (2026). *edf-buffered-write: a buffer-then-flush writer and a
  round-trip integrity test that prevent and detect silent corruption of European
  Data Format recordings.* Software metapaper, Journal of Open Research Software.
- Agis-Torres, Á. (2026). *edf-buffered-write* [Software]. Zenodo.
  https://doi.org/10.5281/zenodo.21163099

A `CITATION.cff` file is provided for automatic citation export.

## Declaration of generative AI

The code in this repository was developed with the assistance of Claude
(Anthropic), and was reviewed and tested by the author.

## License

This repository is dual-licensed:

- **Code** (library, scripts, CI workflow, configuration) under the **MIT License**
  — see `LICENSE`. A permissive licence is deliberate: the buffer-then-flush
  pattern is meant to be copied directly into other acquisition loops.
- **Data** (the two de-identified `.edf` surface-EMG recordings) released into the
  public domain under **CC0-1.0** — see `DATA_LICENSE.md` and
  `LICENSE-CC0-1.0.txt`.
