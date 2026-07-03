import numpy as np, pyedflib, os, warnings
warnings.filterwarnings("ignore")
PMIN,PMAX,DMIN,DMAX=-5.0,5.0,-32768,32767
LSB=(PMAX-PMIN)/(DMAX-DMIN)

def gen(T,fs,nch,seed=42):
    rng=np.random.default_rng(seed)
    t=np.arange(int(T*fs))/fs
    out=np.zeros((nch,len(t)))
    for c in range(nch):
        out[c]=0.3*np.sin(2*np.pi*80*t)+0.05*rng.standard_normal(len(t))
    return out

def hdr(nch,fs):
    return [dict(label=f'ch{i}',dimension='mV',sample_frequency=fs,
                 physical_min=PMIN,physical_max=PMAX,digital_min=DMIN,digital_max=DMAX,
                 transducer='',prefilter='') for i in range(nch)]

def pyedflib_write(path,data,fs,d,block,buffered):
    nch,N=data.shape
    w=pyedflib.EdfWriter(path,nch,file_type=pyedflib.FILETYPE_EDFPLUS)
    w.setSignalHeaders(hdr(nch,fs)); w.setDatarecordDuration(d)
    rec=int(round(fs*d))
    if not buffered:
        for s in range(0,N,block):
            w.writeSamples([np.ascontiguousarray(data[c,s:s+block]) for c in range(nch)])
    else:
        buf=[np.array([],dtype=float) for _ in range(nch)]
        for s in range(0,N,block):
            for c in range(nch): buf[c]=np.concatenate([buf[c],data[c,s:s+block]])
            while len(buf[0])>=rec:
                w.writeSamples([np.ascontiguousarray(buf[c][:rec]) for c in range(nch)])
                for c in range(nch): buf[c]=buf[c][rec:]
        if len(buf[0])>0:
            for c in range(nch):
                pad=np.full(rec-len(buf[c]),buf[c][-1]); buf[c]=np.concatenate([buf[c],pad])
            w.writeSamples([np.ascontiguousarray(buf[c]) for c in range(nch)])
    w.close()

def readback(path):
    r=pyedflib.EdfReader(path); dur=r.file_duration; sig=r.readSignal(0); r.close(); return dur,sig

def metrics(orig_ch0,dur,sig,T):
    rms_o=np.sqrt(np.mean(orig_ch0**2)); rms_r=np.sqrt(np.mean(sig**2))
    pct=100*np.mean(np.abs(sig)<LSB)
    return dur/T, rms_r/rms_o, pct

print("="*74)
print("A) THREE IMPLEMENTATIONS — base config: fs=1000 Hz, record=1 s, block=100, T=10 s, 1 ch")
print("="*74)
data=gen(10,1000,1); orig=data[0]
# pyedflib naive + buffered
pyedflib_write('n.edf',data,1000,1.0,100,False); d,s=readback('n.edf'); inf,rr,pc=metrics(orig,d,s,10)
print(f"pyedflib (EDFlib C-wrapper), NAIVE incremental : duration={d:.0f}s  inflation={inf:.1f}x  RMS_ratio={rr:.3f}  %<1LSB={pc:.1f}")
pyedflib_write('b.edf',data,1000,1.0,100,True); d,s=readback('b.edf'); inf,rr,pc=metrics(orig,d,s,10)
print(f"pyedflib, BUFFERED                             : duration={d:.0f}s  inflation={inf:.1f}x  RMS_ratio={rr:.3f}  %<1LSB={pc:.1f}")
# EDFlib-Python naive
try:
    from EDFlib.edfwriter import EDFwriter
    p='e.edf'
    if os.path.exists(p): os.remove(p)
    w=EDFwriter(p,EDFwriter.EDFLIB_FILETYPE_EDFPLUS,1)
    w.setSampleFrequency(0,1000); w.setPhysicalMaximum(0,PMAX); w.setPhysicalMinimum(0,PMIN)
    w.setDigitalMaximum(0,DMAX); w.setDigitalMinimum(0,DMIN); w.setPhysicalDimension(0,'mV')
    for s0 in range(0,len(orig),100):
        w.writeSamples(np.ascontiguousarray(orig[s0:s0+100]))
    w.close()
    d,s=readback('e.edf'); inf,rr,pc=metrics(orig,d,s,10)
    print(f"EDFlib-Python (pure-Python port), NAIVE incr.  : duration={d:.0f}s  inflation={inf:.1f}x  RMS_ratio={rr:.3f}  %<1LSB={pc:.1f}")
except Exception as ex:
    print("EDFlib-Python test note:",type(ex).__name__,ex)
# edfio (whole-file) — no streaming path
import edfio
es=edfio.EdfSignal(orig, sampling_frequency=1000, label='ch0', physical_range=(PMIN,PMAX))
edfio.Edf([es]).write('io.edf')
d,s=readback('io.edf'); inf,rr,pc=metrics(orig,d,s,10)
print(f"edfio (independent, WHOLE-FILE, no streaming)  : duration={d:.0f}s  inflation={inf:.1f}x  RMS_ratio={rr:.3f}  %<1LSB={pc:.1f}")
print("   -> edfio has no incremental/per-block write API; the pitfall cannot arise.")

print()
print("="*74)
print("B) pyedflib CONFIG SWEEP (naive incremental).  inflation_theory = fs*d / block")
print("="*74)
print(f"{'fs':>6}{'rec_s':>7}{'block':>7}{'nch':>5}{'inflation':>11}{'RMS_ratio':>11}{'%<1LSB':>9}")
sweep=[(256,1.0,32,1),(1000,1.0,100,1),(1000,1.0,100,4),(1000,0.1,10,1),
       (1000,5.0,100,1),(4000,1.0,200,1),(1000,1.0,50,1),(1000,1.0,250,1)]
for fs,d,block,nch in sweep:
    data=gen(10,fs,nch); orig=data[0]
    pyedflib_write('n.edf',data,fs,d,block,False)
    dur,s=readback('n.edf'); inf,rr,pc=metrics(orig,dur,s,10)
    print(f"{fs:>6}{d:>7}{block:>7}{nch:>5}{inf:>10.1f}x{rr:>11.3f}{pc:>9.1f}")
