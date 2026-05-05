"""
write_antipattern.py
====================

Writes a synthetic signal to an EDF+ file using the stream-and-write
ANTIPATTERN: each block of samples received from the device is passed
directly to writeSamples(), without buffering. When the block size is
smaller than the data record duration (one second by default in
pyedflib), the library completes each record by padding with zeros,
silently inflating the file duration and contaminating the signal.

This is the WRONG way to write EDF in real time. It exists in this
package only to demonstrate and quantify the problem — DO NOT use this
pattern in production acquisition software.

Usage as a module
-----------------
    from write_antipattern import write_antipattern
    write_antipattern('out_naive.edf', signal_array)

Usage from the command line
---------------------------
    python write_antipattern.py signal.npy out_naive.edf

Author: Ángel Agis-Torres
License: GPL-3.0
"""

import argparse
import numpy as np
import pyedflib

from generate_signal import FS, BLOCK


def header(fs: int = FS) -> dict:
    """Build the standard EDF signal header used throughout the package."""
    return {
        'label': 'EMG',
        'dimension': 'mV',
        'sample_frequency': fs,
        'physical_min': -5.0,
        'physical_max': 5.0,
        'digital_min': -32768,
        'digital_max': 32767,
        'transducer': '',
        'prefilter': '',
    }


def write_antipattern(path: str,
                      data: np.ndarray,
                      fs: int = FS,
                      block: int = BLOCK) -> None:
    """Write data to an EDF+ file using the stream-and-write antipattern.

    For each block of `block` samples in `data`, a single call to
    writeSamples() is made. When `block` < `fs` (which is the common
    real-time acquisition case), pyedflib pads each call to the full
    record size (one second) with the quantized-zero value, silently
    inflating the file duration and corrupting downstream metrics.

    Parameters
    ----------
    path : str
        Output path for the EDF+ file.
    data : numpy.ndarray
        Signal samples in mV (float64).
    fs : int
        Sampling frequency in Hz.
    block : int
        Block size in samples passed to each writeSamples() call.
    """
    writer = pyedflib.EdfWriter(path, 1, file_type=pyedflib.FILETYPE_EDFPLUS)
    writer.setSignalHeader(0, header(fs))
    try:
        for i in range(0, len(data), block):
            chunk = data[i:i + block].astype(np.float64)
            writer.writeSamples([chunk])
    finally:
        writer.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input', help='path to the .npy signal file '
                                      '(e.g. signal.npy from generate_signal.py)')
    parser.add_argument('output', help='path for the resulting EDF+ file')
    parser.add_argument('--block', type=int, default=BLOCK,
                        help=f'block size in samples (default: {BLOCK})')
    args = parser.parse_args()

    sig = np.load(args.input)
    write_antipattern(args.output, sig, block=args.block)
    print(f'Wrote naive EDF: {args.output}')
    print(f'  Source: {args.input} ({len(sig)} samples, {len(sig)/FS:.1f} s of real signal)')
    print(f'  Block size: {args.block} samples ({args.block*1000//FS} ms)')


if __name__ == '__main__':
    main()
