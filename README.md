# Reproducibility package for: Silent corruption of EDF recordings during real-time biopotential streaming

This repository contains the code, scripts and metric files needed to reproduce
all figures and numerical results reported in the accompanying manuscript,
*Silent corruption of EDF recordings during real-time biopotential streaming: a
buffered-write solution* (under review).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20042878.svg)](https://doi.org/10.5281/zenodo.20042878)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## What this package shows

A common antipattern in real-time biopotential acquisition with `pyedflib`,
calling `writeSamples()` once per device read with fewer samples than the EDF
data record, silently produces files that are an order of magnitude longer
than the actual recording, with attenuated RMS amplitude and severely distorted
power spectral density. This package quantifies the effect on a synthetic EMG
signal and demonstrates a buffered-write pattern that eliminates the artefact.

## Requirements

- Python 3.10 or newer
- See `requirements.txt` for exact pinned versions of all dependencies

```bash
python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Reproduce the figures and metrics in the paper

```bash
# Generate the synthetic signal, write the two EDF files, compute metrics
cd src
python generate_signal.py
python write_antipattern.py signal.npy naive.edf
python write_buffered.py signal.npy buffered.edf
python analyze_files.py signal.npy naive.edf buffered.edf --output ../results/metrics.json

# Generate the four manuscript figures (regenerates the EDF files internally)
python make_figures.py --output ../results/figures
```

Outputs land in `results/figures/` and `results/metrics.json`. Compare the
latter against the values reported in the paper:

| Quantity                                      | Antipattern | Buffered |
|-----------------------------------------------|-------------|----------|
| Reported file duration (s)                    | 100.0       | 10.0     |
| Read-back RMS amplitude (mV)                  | 0.069       | 0.218    |
| Samples within ±1 LSB of zero (%)             | 90.0        | 0.1      |
| PSD attenuation factor at 80 Hz (vs original) | ×51         | ×1.0     |

The signal generator uses a fixed random seed (`np.random.seed(42)`) so that
all numerical results are byte-exact reproducible across machines.

## Power spectral density protocol

Welch's method is applied to the first 2 seconds of each signal, with
1024-sample segments and 50% overlap, on the read-back signal in physical units
(mV). The attenuation factor reported above is the ratio between the PSD values
at 80 Hz computed for the original in-memory signal and for the antipattern
file.

## How to cite

If you use this code, please cite both the article and the software:

- Agis-Torres, Á. (2026). Silent corruption of EDF recordings during real-time
  biopotential streaming: a buffered-write solution. Manuscript under review.
- Agis-Torres, Á. (2026). edf-buffered-write (Version 1.0.1) [Software].
  Zenodo. https://doi.org/10.5281/zenodo.20107850
A `CITATION.cff` file is provided for automatic citation export from GitHub.

## Declaration of generative AI

The Python scripts in this repository were developed with the assistance of
Claude (Anthropic), and were reviewed and tested by the author.

## License

GPL-3.0. See `LICENSE`.
