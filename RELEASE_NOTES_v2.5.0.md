## edf-buffered-write v2.5.0

Packaging and metadata improvements following editorial feedback. No change to
the library, tests or CI.

### Added
- **PyPI packaging.** `pyproject.toml` now carries PyPI classifiers and a
  Homepage URL, so the library can be published to PyPI (`pip install
  edf-buffered-write`).

### Fixed
- **Version string.** `edf_buffered_write.__version__` reported `2.3.0` while the
  package was released as `2.4.0`; both are now `2.5.0`.

### Changed
- **Licensing made explicit.** The README states, up front, that the software
  (the `edf_buffered_write` library and all scripts) is under the **MIT License**
  and the two de-identified `.edf` recordings are under **CC0-1.0**, and points to
  `DATA_LICENSE.md` for the exact file-by-file coverage.
- **Neutral manuscript reference.** `CITATION.cff`, the README and `.zenodo.json`
  no longer name a specific journal; the accompanying manuscript is cited by its
  descriptive title as "submitted".

The Zenodo concept DOI [10.5281/zenodo.21163099](https://doi.org/10.5281/zenodo.21163099)
continues to resolve to the latest version.
