"""
analyze_files.py
================

Reads two EDF+ files (the naive antipattern output and the buffered
recommended-pattern output) and computes the four key metrics reported
in the manuscript:

  1. File duration as reported by pyedflib
  2. Read-back amplitude RMS
  3. Fraction of samples within one LSB of zero (proxy for padding)
  4. Power spectral density attenuation at the dominant frequency

Results are printed to stdout in a human-readable form and (optionally)
saved to a JSON file for later comparison or auditing.

Usage as a module
-----------------
    from analyze_files import analyze
    results = analyze('out_naive.edf', 'out_buffered.edf', original_signal)

Usage from the command line
---------------------------
    python analyze_files.py signal.npy out_naive.edf out_buffered.edf
    python analyze_files.py signal.npy out_naive.edf out_buffered.edf \\
        --output results.json

Author: Ángel Agis-Torres
License: GPL-3.0
"""

import argparse
import json
import os
import numpy as np
import pyedflib
from scipy.signal import welch

from generate_signal import FS


# Quantization threshold: 1.5x the least significant bit of the ADC
# (5 V full scale, 16-bit signed) gives a robust 'effectively zero' marker
QUANT_THRESHOLD = 5.0 / (2 * 32768) * 1.5

# Dominant frequency of the synthetic signal (where the spectral peak lives)
DOMINANT_FREQ = 80.0


def read_back(path: str) -> tuple[np.ndarray, float, float]:
    """Open an EDF file and return (signal, sampling_frequency, duration).

    Parameters
    ----------
    path : str
        Path to an EDF+ file.

    Returns
    -------
    signal : numpy.ndarray
        First channel of the file, in physical units (mV).
    fs : float
        Sampling frequency reported by the file.
    duration : float
        File duration in seconds reported by the file.
    """
    reader = pyedflib.EdfReader(path)
    try:
        signal = reader.readSignal(0)
        fs = reader.getSampleFrequency(0)
        duration = reader.file_duration
        return signal, fs, duration
    finally:
        reader.close()


def psd_at(freq: float, signal: np.ndarray, fs: float = FS,
           nperseg: int = 1024) -> float:
    """Return the PSD value at the frequency bin closest to `freq`."""
    n_win = min(int(fs * 2), len(signal))
    f, p = welch(signal[:n_win], fs=fs, nperseg=nperseg)
    idx = int(np.argmin(np.abs(f - freq)))
    return float(p[idx])


def analyze(naive_path: str,
            buffered_path: str,
            original: np.ndarray) -> dict:
    """Run the full analysis comparing both EDF files to the original signal.

    Parameters
    ----------
    naive_path : str
        Path to the EDF file produced by the antipattern.
    buffered_path : str
        Path to the EDF file produced by the recommended pattern.
    original : numpy.ndarray
        Original synthetic signal (in memory) used as the ground truth.

    Returns
    -------
    dict
        Dictionary with all metrics, ready for JSON serialization.
    """
    naive, _, naive_dur = read_back(naive_path)
    buff, _, buff_dur = read_back(buffered_path)
    real_dur = len(original) / FS

    # 1. RMS amplitude
    orig_rms = float(np.sqrt(np.mean(original ** 2)))
    naive_rms = float(np.sqrt(np.mean(naive ** 2)))
    buff_rms = float(np.sqrt(np.mean(buff ** 2)))

    # 2. Fraction of padded (near-zero) samples
    naive_pad_pct = 100.0 * float(np.sum(np.abs(naive) < QUANT_THRESHOLD)) / len(naive)
    buff_pad_pct = 100.0 * float(np.sum(np.abs(buff) < QUANT_THRESHOLD)) / len(buff)

    # 3. PSD attenuation at the dominant frequency
    psd_orig_80 = psd_at(DOMINANT_FREQ, original)
    psd_naive_80 = psd_at(DOMINANT_FREQ, naive)
    psd_buff_80 = psd_at(DOMINANT_FREQ, buff)

    return {
        'metadata': {
            'pyedflib_version': pyedflib.__version__,
            'fs_hz': FS,
            'real_duration_s': real_dur,
            'quant_threshold_mv': QUANT_THRESHOLD,
            'dominant_freq_hz': DOMINANT_FREQ,
        },
        'duration': {
            'real_s': real_dur,
            'naive_s': float(naive_dur),
            'buffered_s': float(buff_dur),
            'naive_inflation_factor': float(naive_dur / real_dur),
        },
        'rms_mv': {
            'original': orig_rms,
            'naive': naive_rms,
            'buffered': buff_rms,
            'naive_attenuation_factor': orig_rms / naive_rms,
        },
        'padded_fraction_pct': {
            'naive': naive_pad_pct,
            'buffered': buff_pad_pct,
        },
        'spectral_psd_mv2_per_hz_at_80Hz': {
            'original': psd_orig_80,
            'naive': psd_naive_80,
            'buffered': psd_buff_80,
            'naive_attenuation_factor': psd_orig_80 / psd_naive_80,
        },
    }


def print_report(results: dict) -> None:
    """Print a human-readable report of the analysis."""
    md = results['metadata']
    dur = results['duration']
    rms = results['rms_mv']
    pad = results['padded_fraction_pct']
    psd = results['spectral_psd_mv2_per_hz_at_80Hz']

    print('=' * 60)
    print('EDF writing patterns — comparative analysis')
    print('=' * 60)
    print(f'  pyedflib version:           {md["pyedflib_version"]}')
    print(f'  sampling frequency:         {md["fs_hz"]} Hz')
    print(f'  real signal duration:       {md["real_duration_s"]:.1f} s')
    print()
    print('Reported file duration')
    print(f'  Real:                       {dur["real_s"]:.1f} s')
    print(f'  Naive (antipattern):        {dur["naive_s"]:.1f} s '
          f'(x{dur["naive_inflation_factor"]:.1f} inflation)')
    print(f'  Buffered (recommended):     {dur["buffered_s"]:.1f} s')
    print()
    print('Read-back RMS')
    print(f'  Original signal:            {rms["original"]:.4f} mV')
    print(f'  Naive (antipattern):        {rms["naive"]:.4f} mV '
          f'(x{rms["naive_attenuation_factor"]:.2f} attenuation)')
    print(f'  Buffered (recommended):     {rms["buffered"]:.4f} mV')
    print()
    print('Fraction of samples near zero (padding indicator)')
    print(f'  Naive (antipattern):        {pad["naive"]:.1f} %')
    print(f'  Buffered (recommended):     {pad["buffered"]:.1f} %')
    print()
    print('Power spectral density at 80 Hz')
    print(f'  Original signal:            {psd["original"]:.3e} mV^2/Hz')
    print(f'  Naive (antipattern):        {psd["naive"]:.3e} mV^2/Hz '
          f'(x{psd["naive_attenuation_factor"]:.0f} attenuation)')
    print(f'  Buffered (recommended):     {psd["buffered"]:.3e} mV^2/Hz')
    print('=' * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('signal', help='original signal (.npy) used as ground truth')
    parser.add_argument('naive_edf', help='EDF file written with the antipattern')
    parser.add_argument('buffered_edf', help='EDF file written with the buffered pattern')
    parser.add_argument('--output', '-o', default=None,
                        help='optional path to save results as JSON')
    args = parser.parse_args()

    original = np.load(args.signal)
    results = analyze(args.naive_edf, args.buffered_edf, original)
    print_report(results)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f'\nResults saved to: {args.output}')


if __name__ == '__main__':
    main()
