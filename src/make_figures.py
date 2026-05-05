"""
make_figures.py
===============

Generates the four figures of the manuscript at high resolution (300 dpi),
using the standard editorial greyscale palette suitable for biomedical
journals. The figures use the new numbering scheme aligned with the order
in which they are referenced in the text:

  Figure 1. Side-by-side pseudocode of antipattern and recommended pattern
  Figure 2. First 5 s of each EDF file as read back
  Figure 3. Quantitative consequences of the problem
  Figure 4. Power spectral density (Welch)

This module performs the full pipeline end-to-end (signal generation, EDF
writing with both patterns, analysis and figure rendering) and saves the
figures as both PDF (vectorial, for journal submission) and PNG (raster,
for previews and presentations).

Usage as a module
-----------------
    from make_figures import make_all
    make_all(output_dir='./figs')

Usage from the command line
---------------------------
    python make_figures.py                 # writes to ./figs
    python make_figures.py --output ./out  # writes to ./out
    python make_figures.py --formats png   # only PNG (no PDF)

Author: Ángel Agis-Torres
License: GPL-3.0
"""

import argparse
import os
import tempfile

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.signal import welch

from generate_signal import generate, FS, BLOCK, DURATION
from write_antipattern import write_antipattern
from write_buffered import write_buffered
from analyze_files import read_back, QUANT_THRESHOLD


# Editorial style: greyscale, serif font, minimal frames
# Suitable for Elsevier, IEEE and similar biomedical journal templates
mpl.rcParams.update({
    'font.family': 'DejaVu Serif',
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
    'figure.facecolor': 'white',
})


# ----------------------------------------------------------------------------
# Figure 1 — Side-by-side pseudocode (renders the algorithm as a code diagram)
# ----------------------------------------------------------------------------
def make_figure_1(output_dir: str, formats: list[str]) -> None:
    """Side-by-side pseudocode of antipattern and recommended pattern."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))

    naive_code = (
        '# Antipattern: stream-and-write\n'
        'writer = EdfWriter(path, ...)\n'
        '\n'
        'while acquiring:\n'
        '    block = device.read(100)\n'
        '    writer.writeSamples([block])\n'
        '\n'
        'writer.close()'
    )

    buffered_code = (
        '# Recommended: buffer-then-flush\n'
        'writer = EdfWriter(path, ...)\n'
        'buf = np.array([])\n'
        '\n'
        'while acquiring:\n'
        '    block = device.read(100)\n'
        '    buf = np.concatenate([buf, block])\n'
        '    while len(buf) >= fs:\n'
        '        writer.writeSamples([buf[:fs]])\n'
        '        buf = buf[fs:]\n'
        '\n'
        '# flush remainder with last-value padding\n'
        'if len(buf) > 0:\n'
        '    pad = np.full(fs - len(buf), buf[-1])\n'
        '    tail = np.concatenate([buf, pad])\n'
        '    writer.writeSamples([tail])\n'
        'writer.close()'
    )

    panels = [
        (axes[0], naive_code, '(a) Antipattern', '#F9F9F7'),
        (axes[1], buffered_code, '(b) Recommended pattern', '#F3F6F1'),
    ]
    for ax, code, title, fill in panels:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, fc=fill, ec='0.6',
                                   linewidth=0.8, transform=ax.transAxes))
        ax.text(0.5, 1.06, title, ha='center', transform=ax.transAxes,
                fontsize=10, fontweight='bold')
        ax.text(0.04, 0.95, code, transform=ax.transAxes,
                va='top', ha='left', family='monospace', fontsize=8.2)

    plt.tight_layout()
    base = os.path.join(output_dir, 'Figure_1_pseudocode')
    for fmt in formats:
        fig.savefig(f'{base}.{fmt}', format=fmt)
    plt.close(fig)
    print('  Figure 1 (pseudocode) — OK')


# ----------------------------------------------------------------------------
# Figure 2 — First 5 s of each EDF file as read back
# ----------------------------------------------------------------------------
def make_figure_2(output_dir: str, formats: list[str],
                  naive: np.ndarray, buff: np.ndarray) -> None:
    """First 5 s of each EDF file as read back from disk."""
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=False)

    # Top panel: naive antipattern
    ax = axes[0]
    t_naive = np.arange(len(naive)) / FS
    mask = t_naive < 5
    ax.plot(t_naive[mask], naive[mask], color='0.2', linewidth=0.6)
    ax.set_xlim(0, 5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_ylabel('Amplitude (mV)')
    ax.set_title('(a) Streaming without buffering: one write per 100-sample block',
                 loc='left', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.25, linewidth=0.5)
    ax.annotate('100 ms of real data', xy=(0.05, 0.35), xytext=(0.6, 0.42),
                fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.7, color='0.3'))
    ax.annotate('900 ms of silent pad', xy=(0.5, 0.0), xytext=(1.2, -0.35),
                fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.7, color='0.3'))

    # Bottom panel: buffered pattern
    ax = axes[1]
    t_buff = np.arange(len(buff)) / FS
    ax.plot(t_buff, buff, color='0.2', linewidth=0.6)
    ax.set_xlim(0, 5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('Time in the resulting EDF file (s)')
    ax.set_ylabel('Amplitude (mV)')
    ax.set_title('(b) Streaming with buffered writes: one write per full data record',
                 loc='left', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.25, linewidth=0.5)

    plt.tight_layout()
    base = os.path.join(output_dir, 'Figure_2_first_5s')
    for fmt in formats:
        fig.savefig(f'{base}.{fmt}', format=fmt)
    plt.close(fig)
    print('  Figure 2 (first 5 s) — OK')


# ----------------------------------------------------------------------------
# Figure 3 — Quantitative consequences (three subplots: duration, RMS, padding)
# ----------------------------------------------------------------------------
def make_figure_3(output_dir: str, formats: list[str],
                  signal_mv: np.ndarray,
                  naive: np.ndarray, buff: np.ndarray) -> None:
    """Quantitative consequences of the problem: duration, RMS, padding."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6))
    labels = ['Naive', 'Buffered']

    # (a) File duration
    ax = axes[0]
    durations = [len(naive) / FS, len(buff) / FS]
    bars = ax.bar(labels, durations, color=['0.55', '0.25'], width=0.5)
    ax.axhline(DURATION, color='0.1', linestyle=':', linewidth=1)
    ax.text(0.02, DURATION + 4, 'real duration (10 s)', fontsize=8,
            transform=ax.get_yaxis_transform())
    ax.set_ylabel('Reported duration (s)')
    ax.set_title('(a) File duration', loc='left', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 120)
    for b, v in zip(bars, durations):
        ax.text(b.get_x() + b.get_width() / 2, v + 4, f'{v:.0f}',
                ha='center', fontsize=9)

    # (b) Read-back RMS
    ax = axes[1]
    orig_rms = float(np.sqrt(np.mean(signal_mv ** 2)))
    naive_rms = float(np.sqrt(np.mean(naive ** 2)))
    buff_rms = float(np.sqrt(np.mean(buff ** 2)))
    bars = ax.bar(labels, [naive_rms, buff_rms], color=['0.55', '0.25'], width=0.5)
    ax.axhline(orig_rms, color='0.1', linestyle=':', linewidth=1,
               label=f'original RMS = {orig_rms:.3f} mV')
    ax.set_ylabel('Read-back RMS (mV)')
    ax.set_title('(b) Amplitude', loc='left', fontsize=10, fontweight='bold')
    ax.legend(loc='upper left', frameon=False, fontsize=8)
    ax.set_ylim(0, 0.28)
    for b, v in zip(bars, [naive_rms, buff_rms]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f'{v:.3f}',
                ha='center', fontsize=9)

    # (c) Quantized-zero fraction
    ax = axes[2]
    naive_pad = 100 * np.sum(np.abs(naive) < QUANT_THRESHOLD) / len(naive)
    buff_pad = 100 * np.sum(np.abs(buff) < QUANT_THRESHOLD) / len(buff)
    bars = ax.bar(labels, [naive_pad, buff_pad], color=['0.55', '0.25'], width=0.5)
    ax.set_ylabel('Padded samples (%)')
    ax.set_title('(c) Quantized-zero fraction', loc='left',
                 fontsize=10, fontweight='bold')
    ax.set_ylim(0, 100)
    for b, v in zip(bars, [naive_pad, buff_pad]):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f'{v:.1f}%',
                ha='center', fontsize=9)

    plt.tight_layout()
    base = os.path.join(output_dir, 'Figure_3_quantitative')
    for fmt in formats:
        fig.savefig(f'{base}.{fmt}', format=fmt)
    plt.close(fig)
    print('  Figure 3 (quantitative) — OK')


# ----------------------------------------------------------------------------
# Figure 4 — Power spectral density (Welch's method, overlaid PSDs)
# ----------------------------------------------------------------------------
def make_figure_4(output_dir: str, formats: list[str],
                  signal_mv: np.ndarray,
                  naive: np.ndarray, buff: np.ndarray) -> None:
    """Spectral contamination caused by silent padding (Welch PSD)."""
    n_win = FS * 2  # two-second window for the Welch estimate
    f_orig, p_orig = welch(signal_mv[:n_win], fs=FS, nperseg=1024)
    f_naive, p_naive = welch(naive[:n_win], fs=FS, nperseg=1024)
    f_buff, p_buff = welch(buff[:n_win], fs=FS, nperseg=1024)

    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    ax.semilogy(f_orig, p_orig, color='0.1', linewidth=1.2,
                label='original signal', linestyle='-')
    ax.semilogy(f_buff, p_buff, color='0.45', linewidth=1.0,
                label='buffered EDF', linestyle='--')
    ax.semilogy(f_naive, p_naive, color='0.6', linewidth=1.0,
                label='naive EDF', linestyle=':')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('PSD (mV²/Hz)')
    ax.set_xlim(0, 200)
    ax.set_title('Spectral contamination caused by silent padding',
                 loc='left', fontsize=10, fontweight='bold')
    ax.legend(frameon=False, loc='lower left')
    ax.grid(True, alpha=0.25, linewidth=0.5)

    plt.tight_layout()
    base = os.path.join(output_dir, 'Figure_4_PSD')
    for fmt in formats:
        fig.savefig(f'{base}.{fmt}', format=fmt)
    plt.close(fig)
    print('  Figure 4 (PSD) — OK')


# ----------------------------------------------------------------------------
# Orchestrator
# ----------------------------------------------------------------------------
def make_all(output_dir: str = './figs',
             formats: list[str] = None) -> None:
    """Generate all four figures end-to-end.

    Generates the synthetic signal, writes both EDF files in a temporary
    directory, reads them back, and renders the four manuscript figures.

    Parameters
    ----------
    output_dir : str
        Directory where the figures will be saved (created if missing).
    formats : list of str
        Output formats (default: ['pdf', 'png']).
    """
    if formats is None:
        formats = ['pdf', 'png']
    os.makedirs(output_dir, exist_ok=True)

    print(f'Generating figures in {output_dir}/')
    print(f'  Formats: {", ".join(formats)}')

    # 1. Generate synthetic signal
    signal_mv = generate()

    # 2. Write both EDF files in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        path_naive = os.path.join(tmpdir, 'naive.edf')
        path_buff = os.path.join(tmpdir, 'buffered.edf')
        write_antipattern(path_naive, signal_mv)
        write_buffered(path_buff, signal_mv)

        # 3. Read both files back
        naive, _, _ = read_back(path_naive)
        buff, _, _ = read_back(path_buff)

    # 4. Render figures
    make_figure_1(output_dir, formats)
    make_figure_2(output_dir, formats, naive, buff)
    make_figure_3(output_dir, formats, signal_mv, naive, buff)
    make_figure_4(output_dir, formats, signal_mv, naive, buff)

    print(f'\nAll figures saved to {output_dir}/')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', '-o', default='./figs',
                        help='output directory (default: ./figs)')
    parser.add_argument('--formats', nargs='+', default=['pdf', 'png'],
                        choices=['pdf', 'png', 'svg'],
                        help='output formats (default: pdf png)')
    args = parser.parse_args()

    make_all(output_dir=args.output, formats=args.formats)


if __name__ == '__main__':
    main()
