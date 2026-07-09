import wave, struct, math, os
import numpy as np

p = r"F:\clone_output.wav"
w = wave.open(p, 'r')
sr = w.getframerate()
nch = w.getnchannels()
sw = w.getsampwidth()
nf = w.getnframes()
dur = nf / sr
raw = w.readframes(nf)
w.close()

samples = np.array(struct.unpack(f'<{len(raw)//2}h', raw), dtype=np.float64)

# 1. Overall stats
rms = math.sqrt(np.mean(samples**2))
peak = np.max(np.abs(samples))
print(f"=== Overall ===")
print(f"sr={sr}Hz, ch={nch}, dur={dur:.1f}s, samples={nf}")
print(f"RMS={rms:.0f}, peak={peak}")

# 2. Per-second energy to find gaps/silence
print(f"\n=== Per-second energy ===")
samples_per_sec = sr
for i in range(int(dur)):
    chunk = samples[i*samples_per_sec:(i+1)*samples_per_sec]
    if len(chunk) == 0:
        break
    chunk_rms = math.sqrt(np.mean(chunk**2))
    chunk_peak = np.max(np.abs(chunk))
    bar = '#' * int(chunk_rms / 200)
    status = "SILENT" if chunk_rms < 100 else ("LOW" if chunk_rms < 500 else "OK")
    print(f"  {i:2d}-{i+1:2d}s: RMS={chunk_rms:6.0f} peak={chunk_peak:6.0f} [{status}] {bar}")

# 3. Detect silence gaps (contiguous runs below threshold)
print(f"\n=== Silence gap detection (threshold RMS<100) ===")
window_ms = 50
window_size = sr * window_ms // 1000
gaps = []
in_gap = False
gap_start = 0
for i in range(0, len(samples), window_size):
    chunk = samples[i:i+window_size]
    if len(chunk) == 0:
        break
    chunk_rms = math.sqrt(np.mean(chunk**2))
    t = i / sr
    if chunk_rms < 100:
        if not in_gap:
            in_gap = True
            gap_start = t
    else:
        if in_gap:
            in_gap = False
            gap_dur = t - gap_start
            if gap_dur > 0.1:  # only report gaps > 100ms
                gaps.append((gap_start, t, gap_dur))
if in_gap:
    gap_dur = len(samples)/sr - gap_start
    if gap_dur > 0.1:
        gaps.append((gap_start, len(samples)/sr, gap_dur))

if gaps:
    total_silence = sum(g[2] for g in gaps)
    print(f"  Found {len(gaps)} silence gaps, total {total_silence:.1f}s out of {dur:.1f}s")
    for gs, ge, gd in gaps:
        print(f"    {gs:.1f}s - {ge:.1f}s ({gd:.1f}s)")
else:
    print(f"  No significant silence gaps found")

# 4. Zero-crossing rate (high ZCR = noisy/garbled)
print(f"\n=== Zero-crossing rate (per second) ===")
for i in range(int(dur)):
    chunk = samples[i*samples_per_sec:(i+1)*samples_per_sec].astype(np.float64)
    if len(chunk) < 2:
        break
    zcr = np.sum(np.diff(np.sign(chunk)) != 0) / len(chunk)
    print(f"  {i:2d}-{i+1:2d}s: ZCR={zcr:.3f} {'<<< HIGH' if zcr > 0.3 else ''}")

# 5. Clipping detection
print(f"\n=== Clipping detection ===")
clip_count = np.sum(np.abs(samples) >= 32767 * 0.99)
print(f"  Clipped samples: {clip_count} ({clip_count/len(samples)*100:.1f}%)")
