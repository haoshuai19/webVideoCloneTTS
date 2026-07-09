import subprocess, json, os, numpy as np

ref = r"C:\Users\Administrator\Desktop\testAudio0626.mp3"

# Get reference audio info
result = subprocess.run(
    ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', ref],
    capture_output=True, text=True, timeout=10
)
info = json.loads(result.stdout)
stream = info['streams'][0]
fmt = info['format']
print(f"=== Reference Audio ===")
print(f"  File: {os.path.basename(ref)} ({os.path.getsize(ref)} bytes)")
print(f"  Duration: {float(fmt['duration']):.1f}s")
print(f"  Sample rate: {stream.get('sample_rate', '?')}Hz")
print(f"  Channels: {stream.get('channels', '?')}")
print(f"  Bitrate: {fmt.get('bit_rate', '?')}")

# Compare with builtin voice synthesis path
# The builtin voices use subprocess (infer_onnx.py) which is a different pipeline
# Cloned voices use voice_cloning_onnx.py which is in-process ONNX

# Key difference: builtin uses --sample-mode fixed with the official script
# Cloned uses our custom ONNX pipeline which may have issues

print(f"\n=== Root Cause Analysis ===")
print(f"Builtin voice: uses official infer_onnx.py subprocess -> high quality")
print(f"Cloned voice: uses custom voice_cloning_onnx.py in-process ONNX -> low quality")
print(f"\nThe cloning ONNX pipeline may have issues in:")
print(f"  1. build_voice_clone_request_rows - token sequence construction")
print(f"  2. _generate_audio_frames - autoregressive generation loop")
print(f"  3. _decode_frames_to_waveform - codec decoding")
print(f"  4. _post_process_audio - resampling/normalization")
