"""
generate_signal.py
==================

Generates a reproducible synthetic surface-EMG-like signal used as test input
for the EDF writing patterns.

The signal is a 10-second, 1 kHz signal composed of an 80 Hz sinusoidal carrier
(amplitude 0.3 mV, representative of the dominant frequency in the surface EMG
power band) plus additive Gaussian noise (sigma = 0.05 mV). The random seed is
fixed so that any user running this script obtains exactly the same waveform,
which is essential for byte-exact reproducibility of the downstream metrics.

Usage as a module
-----------------
    from generate_signal import generate, FS, DURATION, BLOCK
    signal = generate()

Usage from the command line
---------------------------
    python generate_signal.py            # writes signal.npy in cwd
    python generate_signal.py --plot     # also shows a quick preview

Author: Ángel Agis-Torres
License: GPL-3.0
"""

import argparse
import numpy as np


# Parameters fixed by the manuscript. Do not change unless the manuscript
# is updated accordingly.
FS = 1000          # sampling frequency in Hz
DURATION = 10      # signal duration in seconds
BLOCK = 100        # device block size in samples (100 ms at 1 kHz),
                   # representative of typical Bluetooth biopotential
                   # acquisition devices such as BITalino
SEED = 42          # fixed seed for reproducibility


def generate(fs: int = FS,
             duration: int = DURATION,
             seed: int = SEED) -> np.ndarray:
    """Return the reproducible synthetic EMG-like signal (in mV).

    Parameters
    ----------
    fs : int
        Sampling frequency in Hz.
    duration : int
        Signal duration in seconds.
    seed : int
        Random seed for the additive Gaussian noise.

    Returns
    -------
    numpy.ndarray
        One-dimensional float64 array of length fs * duration containing
        the signal in millivolts.
    """
    np.random.seed(seed)
    t = np.arange(fs * duration) / fs
    carrier = 0.3 * np.sin(2 * np.pi * 80 * t)
    noise = 0.05 * np.random.randn(len(t))
    return (carrier + noise).astype(np.float64)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', '-o', default='signal.npy',
                        help='path where the signal array will be saved (default: signal.npy)')
    parser.add_argument('--plot', action='store_true',
                        help='show a preview of the first second of the signal')
    args = parser.parse_args()

    sig = generate()
    np.save(args.output, sig)
    print(f'Generated synthetic signal: {len(sig)} samples '
          f'({len(sig)/FS:.1f} s at {FS} Hz)')
    print(f'  Mean:  {sig.mean():+.6f} mV')
    print(f'  Std:   {sig.std():.6f} mV')
    print(f'  RMS:   {np.sqrt(np.mean(sig**2)):.6f} mV')
    print(f'  Saved to: {args.output}')

    if args.plot:
        import matplotlib.pyplot as plt
        t = np.arange(FS) / FS
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(t, sig[:FS], color='0.2', linewidth=0.7)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude (mV)')
        ax.set_title('First second of the synthetic EMG signal')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    main()
