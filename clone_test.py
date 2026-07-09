import requests, time, os, shutil

BASE = "http://127.0.0.1:8000"
AUDIO = r"F:\FFOutput\32.mp3"
OUT_DIR = "F:\\"
TEXT = "以前用 AI 做原型，最大的问题不是页面不好看，而是好看但不像自己的产品：颜色、按钮、卡片、表格、交互风格都容易跑偏。尤其是在已有产品里新增功能时，原型最重要的不是炫，而是要和现有产品保持一致。所以这次我把自己用 design-generator 生成的 DESIGN.md 接入到 Open Design 里，让 AI 先读懂产品设计规范，再基于规范生成新页面。这个流程更适合产品经理、售前和解决方案同学，用来做内部评审、客户演示和研发沟通。"

# Step 1: Clone
print("Step 1: Cloning voice...")
with open(AUDIO, "rb") as f:
    r = requests.post(f"{BASE}/api/clone-voice",
        files={"audio_file": (os.path.basename(AUDIO), f, "audio/mpeg")},
        data={"voice_name": "design_demo", "reference_text": ""},
        timeout=120)
d = r.json()
if not d.get("success"):
    print(f"Clone FAILED: {d.get('error')}")
    exit(1)
voice_id = d["data"]["voice_id"]
print(f"  Clone OK: {voice_id}")

# Step 2: Synthesize
print("Step 2: Synthesizing...")
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
for i in range(300):
    r = requests.get(f"{BASE}/api/synthesize/{task_id}", timeout=10)
    d = r.json()
    if d.get("success"):
        if d["data"]["status"] == "completed":
            result_url = d["data"]["result_url"]
            src = os.path.join(r"F:\webVideoCloneTTS\outputs", os.path.basename(result_url))
            dst = os.path.join(OUT_DIR, "clone_design_demo.wav")
            if os.path.exists(src):
                shutil.copy2(src, dst)
                size = os.path.getsize(dst)
                print(f"  DONE: {dst} ({size} bytes)")
            else:
                print(f"  WARN: source not found at {src}")
            break
        elif d["data"]["status"] == "failed":
            print(f"  FAILED: {d['data']['error']}")
            break
    time.sleep(1)
else:
    print("  TIMEOUT")
