# Data license

This repository is **dual-licensed**:

- **Software** (all `.py` scripts, the CI workflow and configuration files) is
  licensed under the **GNU General Public License v3.0** — see `LICENSE`.
- **Data** (the de-identified surface-EMG recordings listed below) is released
  into the public domain under the **Creative Commons CC0 1.0 Universal**
  dedication — see `LICENSE-CC0-1.0.txt` or
  <https://creativecommons.org/publicdomain/zero/1.0/>.

## Files covered by CC0-1.0

| File | Description |
|---|---|
| `emgteach_real_sEMG_2ch_1kHz_58s.edf` | De-identified surface-EMG recording, 2 channels, 1 kHz, 58 s (BITalino acquisition chain). |
| `emgteach_real_sEMG_MyoWare_1ch_1kHz_24s.edf` | De-identified surface-EMG recording, 1 channel, 1 kHz, 24 s (Arduino-compatible board with a MyoWare 2.0 sensor). |

Both recordings are the author's own signals, recorded by the author from
himself and released with his consent. Their EDF+ headers contain no
identifiable personal data (all patient sub-fields are set to `X`).

## Attribution

Under CC0, attribution is **not required** — the recordings may be used for any
purpose without permission. If you find them useful, a citation is appreciated
but not obligatory:

> Agis-Torres, Á. (2026). *edf-buffered-write — de-identified surface-EMG
> recordings.* Zenodo. https://doi.org/10.5281/zenodo.21163099.
