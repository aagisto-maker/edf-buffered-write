# edf-buffered-write — reproducibility package

Code, scripts and data to reproduce every figure and numerical result of the
manuscript *"Preventing and detecting silent EDF corruption in real-time
biopotential streaming: a buffer-then-flush writing method and a round-trip
integrity test"* (under review).

[![CI](https://github.com/aagisto-maker/edf-buffered-write/actions/workflows/ci.yml/badge.svg)](https://github.com/aagisto-maker/edf-buffered-write/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21163099.svg)](https://doi.org/10.5281/zenodo.21163099)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

The DOI above is the *concept* DOI and always resolves to the latest version.

## What this package shows

Real-time acquisition software that hands each sub-record device block straight
to an incremental EDF writer (calling `writeSamples()` with fewer samples than
one data record) silently produces a structurally valid EDF+ file that is
inflated by the record-to-block ratio, with attenuated RMS amplitude and a
distorted power spectrum — and no error is raised. This package characterises
the effect and provides two remedies:

1. a **buffer-then-flush** writing pattern that accumulates samples and commits
   only complete records (padding the last record with the final value, not
   zero), and
2. a **round-trip integrity test** that writes a signal of known statistics,
   reads it back and compares duration, RMS amplitude and PSD, independently of
   the writing library.

The effect is quantified across a configuration sweep, compared across three
EDF writers (`pyedflib` and `EDFlib-Python`, both built on van Beelen's EDFlib,
and the independent `edfio`), and reproduced on a real surface-EMG recording.

## Contents

| File | Purpose |
|---|---|
| `harness_multilibrary.py` | Configuration sweep (Table 1) and three-implementation comparison (Table 2). Prints all numbers. Its functions are importable (guarded `main()`). |
| `test_roundtrip.py` | Automated round-trip integrity tests (`pytest`): the naive pattern must corrupt, the buffered pattern must preserve, and the inflation law must hold across configs. |
| `.github/workflows/ci.yml` | Continuous-integration workflow running the tests on Python 3.10–3.12. |
| `make_figures.py` | Regenerates the synthetic-signal figures (time-domain, inflation law, PSD contamination). |
| `make_pseudocode.py` | Regenerates the side-by-side pseudocode figure. |
| `realdata_roundtrip.py` | Round-trip of a real EDF recording through the naive and buffered writers; produces `Fig_realdata_PSD.png`. |
| `emgteach_real_sEMG_2ch_1kHz_58s.edf` | De-identified real surface-EMG recording used for the real-data round-trip (Figure 5). |
| `Fig_*.png` | The five manuscript figures (300 dpi). |
| `requirements.txt` | Pinned dependency versions. |
| `DATA_LICENSE.md` / `LICENSE-CC0-1.0.txt` | Data license (CC0-1.0, public domain) for the de-identified `.edf` recordings, separate from the GPL-3.0 code. |

## Requirements

Python ≥ 3.10.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Reproduce

```bash
# Table 1 (configuration sweep) + Table 2 (three implementations)
python harness_multilibrary.py

# Synthetic-signal figures (time-domain, inflation law, PSD contamination)
python make_figures.py

# Pseudocode figure
python make_pseudocode.py

# Real-data round-trip, using the included de-identified recording
python realdata_roundtrip.py emgteach_real_sEMG_2ch_1kHz_58s.edf 1 100
```

## Testing

The round-trip integrity check is exercised by an automated test suite:

```bash
pip install pytest
pytest -v
```

`test_roundtrip.py` asserts that the naive per-block writer corrupts the
recording (duration inflated by `fs*d/block`, RMS attenuated by its square root,
signal filled with padding), that the buffer-then-flush writer preserves
duration and amplitude, and that the deterministic inflation law holds across a
range of sampling rates, record durations and block sizes. The same tests run
in continuous integration on Python 3.10–3.12 (`.github/workflows/ci.yml`).

All synthetic results use a fixed random seed (42), so the numbers are
reproducible across machines. Base configuration (fs = 1 kHz, 1 s records,
100-sample blocks):

| Quantity                                      | Naive | Buffered |
|-----------------------------------------------|-------|----------|
| Reported file duration (s)                    | 100.0 | 10.0     |
| Read-back RMS amplitude (mV)                  | 0.069 | 0.218    |
| Samples within ±1 LSB of zero (%)             | 90.0  | 0.1      |
| PSD attenuation factor at 80 Hz (vs original) | ×51   | ×1.0     |

## Real surface-EMG recording

`emgteach_real_sEMG_2ch_1kHz_58s.edf` is a **de-identified** EDF+ recording of
surface EMG (2 channels, 1 kHz, 58 s, physical units mV). Its EDF+ header
carries no personal data — all patient sub-fields are `X` (unknown). It is
provided so the real-data round-trip (Figure 5) can be reproduced exactly.

## Power spectral density protocol

Welch's method on the first 2 s of each read-back signal (1024-sample segments,
50 % overlap, physical units mV). The attenuation factor is the ratio of PSD at
80 Hz between the original in-memory signal and the naive file.

## How to cite

- Agis-Torres, Á. (2026). *Preventing and detecting silent EDF corruption in
  real-time biopotential streaming: a buffer-then-flush writing method and a
  round-trip integrity test.* Manuscript under review.
- Agis-Torres, Á. (2026). *edf-buffered-write* [Software]. Zenodo.
  https://doi.org/10.5281/zenodo.21163099

A `CITATION.cff` file is provided for automatic citation export (update its DOI
to `10.5281/zenodo.21163099` if it still points to an earlier deposit).

## Declaration of generative AI

The scripts in this repository were developed with the assistance of Claude
(Anthropic), and were reviewed and tested by the author.

## License

This repository is dual-licensed:

- **Code** (scripts, CI workflow, configuration) under **GPL-3.0** — see `LICENSE`.
- **Data** (the two de-identified `.edf` surface-EMG recordings) released into
  the public domain under **CC0-1.0** — see `DATA_LICENSE.md` and
  `LICENSE-CC0-1.0.txt`.
