"""
write_buffered.py
=================

Writes a synthetic signal to an EDF+ file using the recommended
BUFFER-THEN-FLUSH pattern. The caller maintains a buffer of pending
samples; each device block is concatenated to it, and full data
records (fs samples each) are flushed to disk only when available.
At close, any remainder is padded with the last acquired value (not
zero) to avoid introducing a spectral discontinuity at the file end.

This is the CORRECT way to write EDF in real time when the device
delivers sub-record blocks. The overhead over the antipattern is
negligible (under 2 ms for a 10-second signal on a consumer laptop).

Usage as a module
-----------------
    from write_buffered import write_buffered
    write_buffered('out_buffered.edf', signal_array)

Usage from the command line
---------------------------
    python write_buffered.py signal.npy out_buffered.edf

Author: Ángel Agis-Torres
License: GPL-3.0
"""

import argparse
import numpy as np
import pyedflib

from generate_signal import FS, BLOCK
from write_antipattern import header  # reuse the shared header definition


def write_buffered(path: str,
                   data: np.ndarray,
                   fs: int = FS,
                   block: int = BLOCK) -> None:
    """Write data to an EDF+ file using the buffer-then-flush pattern.

    The function mimics a real-time acquisition loop: it consumes the
    `data` array in chunks of `block` samples (as the device would
    deliver them), accumulates them in a buffer, and flushes one full
    record (`fs` samples) to writeSamples() at a time. At close, any
    remainder is padded with the last sample value to preserve local
    DC level and avoid a step discontinuity.

    Parameters
    ----------
    path : str
        Output path for the EDF+ file.
    data : numpy.ndarray
        Signal samples in mV (float64).
    fs : int
        Sampling frequency in Hz, equal to the samples-per-record.
    block : int
        Block size in samples received per device read.
    """
    writer = pyedflib.EdfWriter(path, 1, file_type=pyedflib.FILETYPE_EDFPLUS)
    writer.setSignalHeader(0, header(fs))
    try:
        buf = np.array([], dtype=np.float64)

        # Simulate the real-time acquisition loop
        for i in range(0, len(data), block):
            incoming = data[i:i + block].astype(np.float64)
            buf = np.concatenate([buf, incoming])

            # Flush as many complete records as the buffer can supply
            while len(buf) >= fs:
                writer.writeSamples([buf[:fs]])
                buf = buf[fs:]

        # Flush remainder with last-value padding
        if len(buf) > 0:
            last_value = buf[-1]
            pad = np.full(fs - len(buf), last_value, dtype=np.float64)
            tail = np.concatenate([buf, pad])
            writer.writeSamples([tail])
    finally:
        writer.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input', help='path to the .npy signal file '
                                      '(e.g. signal.npy from generate_signal.py)')
    parser.add_argument('output', help='path for the resulting EDF+ file')
    parser.add_argument('--block', type=int, default=BLOCK,
                        help=f'simulated device block size (default: {BLOCK})')
    args = parser.parse_args()

    sig = np.load(args.input)
    write_buffered(args.output, sig, block=args.block)
    print(f'Wrote buffered EDF: {args.output}')
    print(f'  Source: {args.input} ({len(sig)} samples, {len(sig)/FS:.1f} s of real signal)')
    print(f'  Block size: {args.block} samples ({args.block*1000//FS} ms)')


if __name__ == '__main__':
    main()
