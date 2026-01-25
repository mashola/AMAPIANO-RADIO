import subprocess
import time
import os

# --- CONFIGURATION ---
IMAGE_PATH = "background.png"  # Local file downloaded by GitHub Action
AUDIO_FOLDER = "music"         # Local folder where songs are stored
STREAM_URL = "rtmp://a.rtmp.youtube.com/live2/"
STREAM_KEY = os.getenv("STREAM_KEY", "m8tq-7gxk-8rg2-8kbe-80bv") 
STATE_FILE = "state.txt"

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
    while True:
        # Get list of downloaded audio files
        audio_files = sorted([f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.wav')])
        if not audio_files:
            print("No audio files found! Waiting...")
            time.sleep(10)
            continue

        current_index = get_last_index()
        
        for i in range(current_index, len(audio_files)):
            file_path = os.path.join(AUDIO_FOLDER, audio_files[i])
            save_index(i)
            
            print(f"Streaming Local File: {audio_files[i]}")

            # FFmpeg Command optimized for local files
            cmd = [
                'ffmpeg',
                '-re',
                '-loop', '1', '-i', IMAGE_PATH,
                '-i', file_path,
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-b:v', '3500k', 
                '-maxrate', '3500k',
                '-bufsize', '7000k',
                '-pix_fmt', 'yuv420p',
                '-g', '60',         # Keyframe every 2 seconds (good for YouTube)
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',
                '-shortest',
                '-f', 'flv', f"{STREAM_URL}{STREAM_KEY}"
            ]

            process = subprocess.Popen(cmd)
            process.wait() 
            
            if i == len(audio_files) - 1:
                save_index(0)

        print("Looping playlist...")
        time.sleep(2)

if __name__ == "__main__":
    start_streaming()
