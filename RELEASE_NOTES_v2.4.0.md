## edf-buffered-write v2.4.0

Relicense the code from GPL-3.0 to the permissive **MIT License**.

### Changed
- **Code licence: GPL-3.0 → MIT.** The buffer-then-flush pattern is designed to
  be copied directly into other real-time acquisition loops; a permissive licence
  removes the copyleft friction and better serves that reuse goal. `LICENSE`,
  `pyproject.toml`, `CITATION.cff`, `.zenodo.json`, `DATA_LICENSE.md` and the
  README updated accordingly.

### Unchanged
- The two de-identified surface-EMG recordings remain in the public domain under
  **CC0-1.0**.
- Library API (`edf_buffered_write.BufferedEdfWriter`), tests and CI are identical
  to v2.3.0.

The Zenodo concept DOI [10.5281/zenodo.21163099](https://doi.org/10.5281/zenodo.21163099)
continues to resolve to the latest version.
