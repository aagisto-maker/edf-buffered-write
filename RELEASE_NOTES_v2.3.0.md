## edf-buffered-write v2.3.0

Ship the buffer-then-flush writer as a reusable, installable library, and make
the deposit consistent with the accompanying software metapaper (Journal of Open
Research Software).

### Added
- **`edf_buffered_write` package** exposing `BufferedEdfWriter`, a drop-in wrapper
  around `pyedflib.EdfWriter` that accepts blocks of any size, commits only
  complete data records, and pads just the final record with the last acquired
  value (not zero).
- **`pyproject.toml`** — the library is now `pip install`-able (`pip install -e .`).
- **`test_buffered_writer.py`** — API tests: no duration inflation, amplitude
  preserved, multichannel, and input validation.

### Changed
- **Continuous integration** now installs the package (`pip install -e .`) and
  runs both test suites (`test_buffered_writer.py` and `test_roundtrip.py`) on
  Python 3.10–3.12.
- **README** rewritten around the library: install and usage quickstart, correct
  figure map (three body figures) and the two de-identified surface-EMG
  recordings; stale references removed.
- **Metadata** (`CITATION.cff`, `.zenodo.json`) bumped to 2.3.0, affiliation
  unified to *Department of Physiology (Faculty of Pharmacy), Universidad
  Complutense de Madrid*, title set to the JORS title, and "under review"
  wording removed.

### Licensing
- Code: **GPL-3.0**. The two de-identified surface-EMG recordings: **CC0-1.0**
  (public domain).

The Zenodo concept DOI [10.5281/zenodo.21163099](https://doi.org/10.5281/zenodo.21163099)
continues to resolve to the latest version.
