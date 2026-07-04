"""Round-trip integrity tests for the buffer-then-flush EDF writer.

These tests encode the library-independent round-trip check described in the
paper: a signal of known statistics is written, read back, and compared in
reported duration, RMS amplitude and near-zero (padding) fraction. The naive
per-block pattern must corrupt the recording; the buffer-then-flush pattern
must preserve it. Run with `pytest`.
"""
import numpy as np
import pytest

from harness_multilibrary import gen, pyedflib_write, readback, metrics

FS, D, BLOCK, T = 1000, 1.0, 100, 10.0  # base config: 10x inflation expected


def _roundtrip(tmp_path, buffered, fs=FS, d=D, block=BLOCK):
    """Write a known signal with the chosen pattern, read it back, return
    (inflation, rms_ratio, pct_below_1LSB)."""
    data = gen(T, fs, 1)
    path = str(tmp_path / ("buffered.edf" if buffered else "naive.edf"))
    pyedflib_write(path, data, fs, d, block, buffered)
    dur, sig = readback(path)
    return metrics(data[0], dur, sig, T)


def test_naive_pattern_corrupts(tmp_path):
    """The naive per-block writer silently inflates the file, attenuates the
    RMS by the square root of the inflation, and fills it with zero padding."""
    inflation, rms_ratio, pct_pad = _roundtrip(tmp_path, buffered=False)
    expected_inflation = FS * D / BLOCK           # 10x
    assert inflation == pytest.approx(expected_inflation, rel=0.02)
    assert rms_ratio == pytest.approx(np.sqrt(BLOCK / (FS * D)), rel=0.05)  # ~0.316
    assert pct_pad > 80                            # ~90% of samples are padding


def test_buffered_pattern_preserves(tmp_path):
    """The buffer-then-flush writer preserves duration and amplitude and
    introduces no zero padding."""
    inflation, rms_ratio, pct_pad = _roundtrip(tmp_path, buffered=True)
    assert inflation == pytest.approx(1.0, abs=0.01)
    assert rms_ratio == pytest.approx(1.0, abs=0.02)
    assert pct_pad < 5


@pytest.mark.parametrize(
    "fs,d,block",
    [(256, 1.0, 32), (1000, 1.0, 100), (1000, 0.1, 10), (4000, 1.0, 200), (1000, 1.0, 250)],
)
def test_inflation_law(tmp_path, fs, d, block):
    """Measured inflation matches the deterministic law fs*d/block across
    sampling rates, record durations and block sizes."""
    inflation, _, _ = _roundtrip(tmp_path, buffered=False, fs=fs, d=d, block=block)
    assert inflation == pytest.approx(fs * d / block, rel=0.02)
