import requests, time, os, shutil, wave, struct, math

BASE = "http://127.0.0.1:8000"
AUDIO = r"C:\Users\Administrator\Desktop\testAudio0626.mp3"
OUT = "F:\\"
TEXT = "最终落地版本，职级权重保留18%，仅微调2个百分点。内测数据很快印证弊端：基层员工首页卡片长期被上级通知、部门指令占满，跨部门平级协作卡片经常被折叠在二级菜单，用户想要找同事消息需要手动点开折叠列表，反而增加操作步骤，反向背离精简效率的设计初衷。"

# Step 1: Clone
print("Step 1: Cloning voice from testAudio.mp3...")
with open(AUDIO, "rb") as f:
    r = requests.post(f"{BASE}/api/clone-voice",
        files={"audio_file": ("testAudio.mp3", f, "audio/mpeg")},
        data={"voice_name": "clone_test", "reference_text": ""},
        timeout=120)
d = r.json()
if not d.get("success"):
    print(f"Clone FAILED: {d.get('error')}")
    exit(1)
voice_id = d["data"]["voice_id"]
print(f"  Clone OK: {voice_id}")

# Step 2: Synthesize
print("Step 2: Synthesizing text...")
r = requests.post(f"{BASE}/api/synthesize", json={
    "text": TEXT, "voice_id": voice_id,
    "format": "wav", "sample_rate": 16000
}, timeout=30)
d = r.json()
if not d.get("success"):
    print(f"Synthesize FAILED: {d.get('error')}")
    exit(1)
task_id = d["data"]["task_id"]
print(f"  Task: {task_id}")

# Step 3: Poll
print("Step 3: Waiting for synthesis...")
for i in range(600):
    r = requests.get(f"{BASE}/api/synthesize/{task_id}", timeout=10)
    d = r.json()
    if d.get("success"):
        if d["data"]["status"] == "completed":
            result_url = d["data"]["result_url"]
            src = os.path.join(r"F:\webVideoCloneTTS\outputs", os.path.basename(result_url))
            dst = os.path.join(OUT, "clone_output.wav")
            if os.path.exists(src):
                shutil.copy2(src, dst)
                # Verify audio
                w = wave.open(dst, 'r')
                sr = w.getframerate()
                nf = w.getnframes()
                dur = nf / sr
                fr = w.readframes(nf)
                w.close()
                s = struct.unpack(f'<{len(fr)//2}h', fr)
                rms = math.sqrt(sum(x*x for x in s) / len(s))
                peak = max(abs(x) for x in s)
                print(f"  DONE: {dst}")
                print(f"  Audio: {sr}Hz, {dur:.1f}s, RMS={rms:.0f}, peak={peak}")
            else:
                print(f"  WARN: source not found at {src}")
            break
        elif d["data"]["status"] == "failed":
            print(f"  FAILED: {d['data']['error']}")
            break
    time.sleep(1)
else:
    print("  TIMEOUT")
