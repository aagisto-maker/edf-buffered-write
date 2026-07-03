# edf-buffered-write — extended reproducibility package (revision)

This directory extends the original `edf-buffered-write` package with the
experiments added for the revised manuscript *"Silent corruption of EDF
recordings during real-time biopotential streaming: a cross-implementation
characterisation and a buffered-write solution"*: a multi-configuration sweep, a
cross-implementation comparison (pyedflib, EDFlib-Python, edfio), and a
round-trip on a real surface-EMG recording.

## Contents

| File | Purpose |
|---|---|
| `harness_multilibrary.py` | Multi-configuration sweep (Table 1) and three-implementation comparison (Table 2). Prints all numbers. |
| `realdata_roundtrip.py` | Round-trip of a real EDF recording through the naive and buffered writers; produces `Fig_realdata_PSD.png`. |
| `make_figures.py` | Regenerates the synthetic-signal figures (time-domain, inflation law, PSD). |
| `Fig_*.png` | Figures used in the manuscript. |
| `RESULTS-batch1.md`, `RESULTS-batch2.md` | Logged numeric results. |

## Requirements

Python ≥ 3.10. See `requirements.txt`:

```
pip install -r requirements.txt
```

## Reproduce

```bash
# Table 1 (config sweep) + Table 2 (three implementations)
python harness_multilibrary.py

# Synthetic-signal figures (time-domain, inflation law, PSD)
python make_figures.py

# Real-data round-trip (Figure 5): provide any valid EDF recording
python realdata_roundtrip.py your_recording.edf 1 100
```

The real surface-EMG recordings used in the paper are not redistributed here for
privacy reasons; they are available from the author on reasonable request. The
round-trip script works with any valid EDF file.

## Figure provenance

`Fig_inflation_law.png` and `Fig_PSD_contamination.png` are reproduced
byte-for-byte by `make_figures.py`; `Fig_timedomain_burst_padding.png` is an
equivalent regeneration (same signal and seed). `Fig_pseudocode.png` is a static
illustration of the pseudocode shown in the paper. `Fig_realdata_PSD.png` is
produced by `realdata_roundtrip.py`.

All results use a fixed random seed, so the numbers are reproducible across
machines.
