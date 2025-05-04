import subprocess


def load_devices(ffmpeg_path):
    print("Loading devices...",ffmpeg_path)
    try:
        result = subprocess.run(
            [ffmpeg_path, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        output = result.stderr
        video_devices = []
        audio_devices = []

        for line in output.splitlines():
            if "video device" in line.lower():
                video_devices.append(line.split(":")[-1].strip())
            if "audio device" in line.lower():
                audio_devices.append(line.split(":")[-1].strip())

        return {"video": video_devices, "audio": audio_devices}
    except Exception as e:
        print(f"Error loading devices: {e}")
        return {"video": [], "audio": []}
