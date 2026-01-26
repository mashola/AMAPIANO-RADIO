import subprocess
import time
import os
import signal

# --- CONFIGURATION ---
IMAGE_PATH = "amapiano.png"
AUDIO_FOLDER = "amapiano"
STREAM_URL = "rtmp://x.rtmp.youtube.com/live2"
STREAM_KEY = "m8tq-7gxk-8rg2-8kbe-80bv" 
STATE_FILE = "state.txt"

# 5 hours and 45 minutes in seconds (to stay under the 6h limit)
MAX_RUNTIME = 20700 
start_time = time.time()

def get_last_index():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return int(f.read().strip())
        except: return 0
    return 0

def save_index(index):
    with open(STATE_FILE, "w") as f:
        f.write(str(index))

def start_streaming():
    full_stream_url = f"{STREAM_URL}/{STREAM_KEY}"
    
    while True:
        # Check if we have exceeded the 5h 45m limit
        if time.time() - start_time > MAX_RUNTIME:
            print("Approaching GitHub 6h limit. Restarting sequence...")
            break

        if not os.path.exists(AUDIO_FOLDER):
            print("Audio folder missing...")
            time.sleep(10)
            continue

        audio_files = sorted([f for f in os.listdir(AUDIO_FOLDER) if f.lower().endswith('.wav')])
        if not audio_files:
            time.sleep(10)
            continue

        current_index = get_last_index()
        if current_index >= len(audio_files):
            current_index = 0

        for i in range(current_index, len(audio_files)):
            # Double check time inside the loop
            if time.time() - start_time > MAX_RUNTIME:
                break

            file_path = os.path.join(AUDIO_FOLDER, audio_files[i])
            save_index(i)
            print(f"Streaming: {audio_files[i]}")

            cmd = [
                'ffmpeg', '-re', '-loop', '1', '-i', IMAGE_PATH,
                '-i', file_path, '-c:v', 'libx264', '-preset', 'veryfast',
                '-b:v', '2500k', '-maxrate', '2500k', '-bufsize', '5000k',
                '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac',
                '-b:a', '128k', '-ar', '44100', '-shortest', '-f', 'flv', 
                full_stream_url
            ]

            process = subprocess.Popen(cmd)
            process.wait() 
            
            if i == len(audio_files) - 1:
                save_index(0)

        time.sleep(2)

if __name__ == "__main__":
    start_streaming()
