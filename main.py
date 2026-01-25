import subprocess
import time
import os

# --- CONFIGURATION ---
IMAGE_PATH = "amapiano.png"
AUDIO_FOLDER = "amapiano"
# Ensure the URL ends with a /
STREAM_URL = "rtmp://x.rtmp.youtube.com/live2/"
# Priority: 1. Environment Secret, 2. Hardcoded fallback
STREAM_KEY = os.getenv("STREAM_KEY", "m8tq-7gxk-8rg2-8kbe-80bv")
STATE_FILE = "state.txt"

def get_last_index():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_index(index):
    with open(STATE_FILE, "w") as f:
        f.write(str(index))

def start_streaming():
    while True:
        # Check if directory exists and get files
        if not os.path.exists(AUDIO_FOLDER):
            print(f"Error: Folder {AUDIO_FOLDER} not found!")
            time.sleep(10)
            continue

        audio_files = sorted([f for f in os.listdir(AUDIO_FOLDER) if f.lower().endswith('.wav')])
        
        if not audio_files:
            print("No audio files found! Waiting...")
            time.sleep(10)
            continue

        current_index = get_last_index()
        
        # If the saved index is out of range (e.g. files were deleted), reset to 0
        if current_index >= len(audio_files):
            current_index = 0

        for i in range(current_index, len(audio_files)):
            file_path = os.path.join(AUDIO_FOLDER, audio_files[i])
            save_index(i)
            
            print(f"Streaming Local File: {audio_files[i]}")

            # FFmpeg Command
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
                '-g', '60',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',
                '-shortest',
                '-f', 'flv', f"{STREAM_URL}{STREAM_KEY}"
            ]

            process = subprocess.Popen(cmd)
            process.wait() 
            
            # Reset index to 0 if we reached the end of the folder
            if i == len(audio_files) - 1:
                save_index(0)

        print("Looping playlist...")
        time.sleep(2)

if __name__ == "__main__":
    start_streaming()
