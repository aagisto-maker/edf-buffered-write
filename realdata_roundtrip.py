#!/usr/bin/env python3
"""Round-trip a REAL EDF recording through the naive vs buffered pyedflib writers.

Usage:  python realdata_roundtrip.py recording.edf [channel_index] [block] [out.png]

Reads one channel from a real EDF file, re-streams it in sub-record blocks with
(a) the naive incremental pattern and (b) the buffered-write pattern, reads both
back, and reports duration inflation, RMS ratio and PSD attenuation. Writes a
power-spectral-density comparison figure (300 dpi) next to this script.

Reproduce the manuscript figures:
  python realdata_roundtrip.py emgteach_real_sEMG_2ch_1kHz_58s.edf 1 100 Fig_realdata_PSD.png
  python realdata_roundtrip.py emgteach_real_sEMG_MyoWare_1ch_1kHz_24s.edf 0 100 Fig_realdata_PSD_MyoWare.png
"""
import sys, os
import numpy as np
import pyedflib
from scipy.signal import welch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt


def main():
    if len(sys.argv) < 2:
        print("usage: python realdata_roundtrip.py recording.edf [ch] [block] [out.png]"); return
    path = sys.argv[1]
    ch = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    block = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    outname = sys.argv[4] if len(sys.argv) > 4 else "Fig_realdata_PSD.png"

    r = pyedflib.EdfReader(path)
    fs = int(round(r.getSampleFrequency(ch)))
    x = r.readSignal(ch)
    label = r.getSignalLabels()[ch]
    pmin, pmax = r.getPhysicalMinimum(ch), r.getPhysicalMaximum(ch)
    r.close()
    T = len(x) / fs
    print(f"Real EDF: {os.path.basename(path)} | ch '{label}' | fs={fs} Hz | {T:.1f} s | {len(x)} samples")

    hdr = [dict(label="ch0", dimension="uV", sample_frequency=fs,
               physical_min=float(pmin), physical_max=float(pmax),
               digital_min=-32768, digital_max=32767, transducer="", prefilter="")]

    def write(pathout, buffered, d=1.0):
        w = pyedflib.EdfWriter(pathout, 1, file_type=pyedflib.FILETYPE_EDFPLUS)
        w.setSignalHeaders(hdr); w.setDatarecordDuration(d)
        rec = int(round(fs * d))
        if not buffered:
            for s in range(0, len(x), block):
                w.writeSamples([np.ascontiguousarray(x[s:s+block])])
        else:
            buf = np.array([])
            for s in range(0, len(x), block):
                buf = np.concatenate([buf, x[s:s+block]])
                while len(buf) >= rec:
                    w.writeSamples([np.ascontiguousarray(buf[:rec])]); buf = buf[rec:]
            if len(buf) > 0:
                buf = np.concatenate([buf, np.full(rec-len(buf), buf[-1])])
                w.writeSamples([np.ascontiguousarray(buf)])
        w.close()

    def readback(p):
        rr = pyedflib.EdfReader(p); d = rr.file_duration; s = rr.readSignal(0); rr.close(); return d, s

    write("real_naive.edf", False); write("real_buffered.edf", True)
    dn, sn = readback("real_naive.edf"); db, sb = readback("real_buffered.edf")
    rms = lambda a: np.sqrt(np.mean(a**2))
    print(f"NAIVE   : duration={dn:.1f}s  inflation={dn/T:.1f}x  RMS_ratio={rms(sn)/rms(x):.3f}")
    print(f"BUFFERED: duration={db:.1f}s  inflation={db/T:.2f}x  RMS_ratio={rms(sb)/rms(x):.3f}")

    nwin = min(fs*4, len(x))
    fo, Po = welch(x[:nwin], fs, nperseg=min(1024, nwin))
    fn, Pn = welch(sn[:nwin], fs, nperseg=min(1024, nwin))
    fb, Pb = welch(sb[:nwin], fs, nperseg=min(1024, nwin))
    plt.figure(figsize=(6, 4))
    plt.semilogy(fo, Po, "k-", lw=1.5, label="original (real)")
    plt.semilogy(fb, Pb, "--", lw=1.2, label="buffered (fix)")
    plt.semilogy(fn, Pn, ":", lw=1.2, label="naive (bug)")
    plt.xlabel("Frequency (Hz)"); plt.ylabel("PSD (mV²/Hz)"); plt.legend()
    plt.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), outname)
    plt.savefig(out, dpi=300); print("figure saved:", out)
    for tmp in ("real_naive.edf", "real_buffered.edf"):
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    main()
