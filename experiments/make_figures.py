#!/usr/bin/env python3
"""Regenerate the synthetic-signal figures of the manuscript.

Produces (deterministically, seed 42):
  - Fig_timedomain_burst_padding.png  (first 5 s: naive bursts+padding vs buffered)
  - Fig_inflation_law.png             (measured inflation vs record/block ratio)
  - Fig_PSD_contamination.png         (PSD: original / buffered / naive)

The real-data figure (Fig_realdata_PSD.png) is produced by realdata_roundtrip.py.
Usage:  python make_figures.py [output_dir]
"""
import sys, os
import numpy as np
import pyedflib
from scipy.signal import welch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
PMIN, PMAX, DMIN, DMAX = -5.0, 5.0, -32768, 32767


def gen(T, fs, seed=42):
    rng = np.random.default_rng(seed)
    t = np.arange(int(T * fs)) / fs
    return 0.3 * np.sin(2 * np.pi * 80 * t) + 0.05 * rng.standard_normal(len(t))


def _hdr(fs):
    return [dict(label="ch0", dimension="mV", sample_frequency=fs,
                 physical_min=PMIN, physical_max=PMAX,
                 digital_min=DMIN, digital_max=DMAX, transducer="", prefilter="")]


def write(path, x, fs, d, block, buffered):
    w = pyedflib.EdfWriter(path, 1, file_type=pyedflib.FILETYPE_EDFPLUS)
    w.setSignalHeaders(_hdr(fs)); w.setDatarecordDuration(d)
    rec = int(round(fs * d))
    if not buffered:
        for s in range(0, len(x), block):
            w.writeSamples([np.ascontiguousarray(x[s:s + block])])
    else:
        buf = np.array([])
        for s in range(0, len(x), block):
            buf = np.concatenate([buf, x[s:s + block]])
            while len(buf) >= rec:
                w.writeSamples([np.ascontiguousarray(buf[:rec])]); buf = buf[rec:]
        if len(buf) > 0:
            w.writeSamples([np.ascontiguousarray(np.concatenate([buf, np.full(rec - len(buf), buf[-1])]))])
    w.close()


def rb(p):
    r = pyedflib.EdfReader(p); d = r.file_duration; s = r.readSignal(0); r.close(); return d, s


def fig_timedomain():
    fs = 1000
    x = gen(10, fs)
    write("n.edf", x, fs, 1.0, 100, False)
    write("b.edf", x, fs, 1.0, 100, True)
    _, sn = rb("n.edf"); _, sb = rb("b.edf")
    t = np.arange(5 * fs) / fs
    fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    ax[0].plot(t, sn[:5 * fs], lw=0.6, color="k")
    ax[0].set_title("(a) Streaming without buffering: one write per 100-sample block")
    ax[0].annotate("100 ms of real data", xy=(0.05, 0.35), xytext=(0.7, 0.42),
                   arrowprops=dict(arrowstyle="->", color="0.4"), fontsize=9)
    ax[0].annotate("900 ms of silent padding", xy=(0.5, 0.0), xytext=(1.2, -0.3),
                   arrowprops=dict(arrowstyle="->", color="0.4"), fontsize=9)
    ax[1].plot(t, sb[:5 * fs], lw=0.6, color="k")
    ax[1].set_title("(b) Streaming with buffered writes: one write per full data record")
    ax[1].set_xlabel("Time in the resulting EDF file (s)")
    for a in ax:
        a.set_ylabel("Amplitude (mV)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "Fig_timedomain_burst_padding.png"), dpi=300)
    plt.close(fig)


def fig_inflation():
    ratios, infl = [], []
    for fs, d, block in [(256, 1, 32), (1000, 1, 250), (1000, 1, 100),
                         (1000, 1, 50), (4000, 1, 200), (1000, 5, 100)]:
        x = gen(10, fs); write("n.edf", x, fs, d, block, False)
        dur, _ = rb("n.edf"); ratios.append(block / (fs * d)); infl.append(dur / 10)
    o = np.argsort(ratios); ratios = np.array(ratios)[o]; infl = np.array(infl)[o]
    plt.figure(figsize=(5, 4)); rr = np.linspace(min(ratios), max(ratios), 100)
    plt.plot(rr, 1 / rr, "k-", lw=1, label="theory: record/block")
    plt.plot(ratios, infl, "o", ms=7, label="measured (pyedflib)")
    plt.xlabel("block / record size"); plt.ylabel("file-duration inflation (×)")
    plt.yscale("log"); plt.xscale("log"); plt.legend()
    plt.title("Silent inflation follows fs·d / block"); plt.tight_layout()
    plt.savefig(os.path.join(OUT, "Fig_inflation_law.png"), dpi=300); plt.close()


def fig_psd():
    fs = 1000; x = gen(10, fs)
    write("n.edf", x, fs, 1, 100, False); write("b.edf", x, fs, 1, 100, True)
    _, sn = rb("n.edf"); _, sb = rb("b.edf"); nwin = 2000
    fo, Po = welch(x[:nwin], fs, nperseg=1024)
    fn, Pn = welch(sn[:nwin], fs, nperseg=1024)
    fb, Pb = welch(sb[:nwin], fs, nperseg=1024)
    plt.figure(figsize=(6, 4))
    plt.semilogy(fo, Po, "k-", lw=1.5, label="original")
    plt.semilogy(fb, Pb, "--", lw=1.2, label="buffered (fix)")
    plt.semilogy(fn, Pn, ":", lw=1.2, label="naive (bug)")
    plt.xlabel("Frequency (Hz)"); plt.ylabel("PSD (mV²/Hz)"); plt.xlim(0, 200)
    plt.legend(); plt.title("Spectral contamination (fs=1 kHz, block=100, record=1 s)")
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "Fig_PSD_contamination.png"), dpi=300); plt.close()


if __name__ == "__main__":
    fig_timedomain(); fig_inflation(); fig_psd()
    for f in ("n.edf", "b.edf"):
        if os.path.exists(f):
            os.remove(f)
    print("figures written to", os.path.abspath(OUT))
