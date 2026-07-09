import psutil
import time
import threading
import requests
import os

BASE = "http://127.0.0.1:8000"

monitor_data = []
monitoring = True

def monitor():
    while monitoring:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                if info['cpu_percent'] > 5 or info['memory_percent'] > 5:
                    procs.append(f"{info['name']}(pid={info['pid']},cpu={info['cpu_percent']:.0f}%,mem={info['memory_percent']:.1f}%)")
            except:
                pass
        monitor_data.append({
            'time': time.strftime('%H:%M:%S'),
            'cpu': cpu,
            'mem_used': round(mem.used / 1024**3, 1),
            'mem_total': round(mem.total / 1024**3, 1),
            'mem_pct': mem.percent,
            'top_procs': procs[:5]
        })

t = threading.Thread(target=monitor, daemon=True)
t.start()

# Step 1: Clone
print("=== Cloning voice ===")
try:
    with open(r"C:\Users\Administrator\Desktop\testAudio.mp3", "rb") as f:
        r = requests.post(f"{BASE}/api/clone-voice",
            files={"audio_file": ("testAudio.mp3", f, "audio/mpeg")},
            data={"voice_name": "monitor_test", "reference_text": ""},
            timeout=120)
    d = r.json()
    print(f"Clone: {d.get('success')} - {d.get('data', {}).get('voice_id', d.get('error', ''))}")
    if d.get('success'):
        voice_id = d['data']['voice_id']
        
        # Step 2: Synthesize with cloned voice
        print("=== Synthesizing with cloned voice ===")
        r = requests.post(f"{BASE}/api/synthesize", json={
            "text": "测试语音克隆效果，今天天气不错",
            "voice_id": voice_id,
            "format": "wav", "sample_rate": 16000
        }, timeout=30)
        d = r.json()
        print(f"Synth task: {d.get('data', {}).get('task_id', d.get('error', ''))}")
        
        if d.get('success'):
            task_id = d['data']['task_id']
            # Wait for completion
            for i in range(180):
                r = requests.get(f"{BASE}/api/synthesize/{task_id}", timeout=10)
                d = r.json()
                status = d.get('data', {}).get('status', '')
                if status in ('completed', 'failed'):
                    print(f"Result: {status}")
                    break
                time.sleep(1)
except Exception as e:
    print(f"Error: {e}")

monitoring = False
time.sleep(1)

# Report
print("\n=== RESOURCE MONITOR ===")
print(f"{'Time':<10} {'CPU%':>5} {'MemUsed':>8} {'MemTotal':>9} {'Mem%':>5}  Top Processes")
print("-" * 100)
for d in monitor_data:
    print(f"{d['time']:<10} {d['cpu']:>5.0f} {d['mem_used']:>7.1f}G {d['mem_total']:>8.1f}G {d['mem_pct']:>5.0f}  {', '.join(d['top_procs'])}")

# Peak stats
peak_cpu = max(d['cpu'] for d in monitor_data)
peak_mem = max(d['mem_pct'] for d in monitor_data)
print(f"\nPeak CPU: {peak_cpu:.0f}%  Peak Memory: {peak_mem:.0f}%")
