import wave, struct, math, os, numpy as np

def analyze(filepath, label):
    w = wave.open(filepath, 'r')
    sr = w.getframerate(); nf = w.getnframes(); dur = nf/sr
    raw = w.readframes(nf); w.close()
    s = np.array(struct.unpack(f'<{len(raw)//2}h', raw), dtype=np.float64)

    # FFT on first 2 seconds to see frequency spectrum
    chunk = s[:sr*2]
    fft = np.abs(np.fft.rfft(chunk))
    freqs = np.fft.rfftfreq(len(chunk), 1/sr)

    # Energy in bands
    bands = [(0,500,"低频"), (500,2000,"中频"), (2000,4000,"中高频"), (4000,8000,"高频")]
    total_energy = np.sum(fft**2)
    print(f"\n=== {label} ===")
    print(f"  dur={dur:.1f}s sr={sr} samples={nf}")
    for lo, hi, name in bands:
        mask = (freqs >= lo) & (freqs < hi)
        energy = np.sum(fft[mask]**2) / total_energy * 100
        print(f"  {name}({lo}-{hi}Hz): {energy:.1f}%")

    # Spectral centroid (brightness)
    sc = np.sum(freqs * fft) / np.sum(fft)
    print(f"  频谱重心: {sc:.0f}Hz {'(偏低-含糊)' if sc < 800 else '(正常)'}")

    # Signal-to-noise ratio estimate
    noise_floor = np.median(np.abs(s[:sr//10]))  # first 100ms
    signal_level = np.median(np.abs(s[sr:sr*2]))  # second 1s
    snr = 20 * math.log10(signal_level / (noise_floor + 1))
    print(f"  信噪比估计: {snr:.1f}dB {'(差)' if snr < 10 else '(一般)' if snr < 20 else '(好)'}")

    return dur, sc

# Compare cloned vs builtin
clone_d, clone_sc = analyze(r"F:\clone_output.wav", "克隆音色")
builtin_path = r"F:\webVideoCloneTTS\outputs\tts_M_01_xiaoyuan.wav"
if os.path.exists(builtin_path):
    builtin_d, builtin_sc = analyze(builtin_path, "内置音色(小媛)")

    print(f"\n=== 对比 ===")
    print(f"  时长: 克隆={clone_d:.1f}s vs 内置={builtin_d:.1f}s")
    print(f"  频谱重心: 克隆={clone_sc:.0f}Hz vs 内置={builtin_sc:.0f}Hz")
    print(f"  差异: {'克隆音频频谱重心偏低，声音含糊' if clone_sc < builtin_sc * 0.7 else '频谱接近'}")
