import customtkinter as ctk
from tkinter import messagebox
import subprocess, os, time, json
from utils.device_utils import load_devices
from utils.logger import log
from datetime import datetime

OBS_PATH = r"C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe"
OBS_OUTPUT_FILE = os.path.expanduser("~\\AppData\\Roaming\\obs-studio\\basic\\profiles\\Untitled\\obs-multi-rtmp.json")
OBS_SERVICE_FILE = os.path.expanduser("~\\AppData\\Roaming\\obs-studio\\basic\\profiles\\Untitled\\service.json")
KEY_FILE = "stream_keys.json"
LOG_FILE = "stream_log.txt"
FFMPEG_PATH = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")

class StreamApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔴 Multi Stream Manager")
        self.geometry("500x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.obs_process = None
        self.streaming_start_time = None
        self.test_mode = ctk.BooleanVar()

        self.audio_devices = []
        self.video_devices = []

        self.create_widgets()
        self.load_keys()
        log("App started")
        self.load_devices()

    def create_widgets(self):
        ctk.CTkLabel(self, text="YouTube Stream Key:").pack(pady=(20, 5))
        self.yt_entry = ctk.CTkEntry(self, width=400)
        self.yt_entry.pack()

        ctk.CTkLabel(self, text="Facebook Stream Key:").pack(pady=(20, 5))
        self.fb_entry = ctk.CTkEntry(self, width=400)
        self.fb_entry.pack()

        ctk.CTkLabel(self, text="Select Camera:").pack(pady=(20, 5))
        self.camera_combo = ctk.CTkComboBox(self, values=[])
        self.camera_combo.pack()

        ctk.CTkLabel(self, text="Select Microphone:").pack(pady=(20, 5))
        self.microphone_combo = ctk.CTkComboBox(self, values=[])
        self.microphone_combo.pack()

        self.test_checkbox = ctk.CTkCheckBox(self, text="Test Mode (OBS won't launch)", variable=self.test_mode)
        self.test_checkbox.pack(pady=10)

        self.start_btn = ctk.CTkButton(self, text="▶️ Start Streaming", command=self.start_stream)
        self.start_btn.pack(pady=10)

        self.stop_btn = ctk.CTkButton(self, text="⛔ Stop Streaming", command=self.stop_stream, fg_color="red")
        self.stop_btn.pack(pady=10)
        self.stop_btn.configure(state="disabled")

        self.timer_label = ctk.CTkLabel(self, text="00:00:00")
        self.timer_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Status: Ready", text_color="green")
        self.status_label.pack(pady=10)

    def load_devices(self):
        devices = load_devices(FFMPEG_PATH)
        self.video_devices = devices["video"]
        self.audio_devices = devices["audio"]

        self.camera_combo.configure(values=self.video_devices)
        self.microphone_combo.configure(values=self.audio_devices)

        if self.video_devices:
            self.camera_combo.set(self.video_devices[0])
        if self.audio_devices:
            self.microphone_combo.set(self.audio_devices[0])

        log(f"Video devices: {self.video_devices}")
        log(f"Audio devices: {self.audio_devices}")

    def start_stream(self):
        yt_key = self.yt_entry.get().strip()
        fb_key = self.fb_entry.get().strip()

        if not yt_key or not fb_key:
            messagebox.showerror("Error", "Please enter both stream keys.")
            return

        self.save_keys(yt_key, fb_key)
        self.write_youtube_output(yt_key)
        self.write_facebook_service(fb_key)
        self.configure_obs_sources()

        self.start_obs()

        self.streaming_start_time = time.time()
        self.update_timer()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Status: Streaming...", text_color="green")
        log("Streaming started")

    def stop_stream(self):
        if self.obs_process:
            self.obs_process.terminate()
            self.obs_process = None
        self.status_label.configure(text="Status: Stopped", text_color="red")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        log("Streaming stopped")
        messagebox.showinfo("Info", "Streaming stopped successfully.")

    def start_obs(self):
        if not os.path.exists(OBS_PATH):
            messagebox.showerror("Error", "OBS path not found.")
            return

        if self.test_mode.get():
            log("Test mode enabled, OBS will not start.")
            messagebox.showinfo("Info", "Test mode enabled, OBS will not start.")
            return

        if self.obs_process:
            self.obs_process.terminate()

        self.obs_process = subprocess.Popen([OBS_PATH], cwd=os.path.dirname(OBS_PATH))

    def write_youtube_output(self, yt_key):
        outputs = {
            "audio_configs": [],
            "targets": [
                {
                    "id": "1835122281",
                    "name": "Youtube",
                    "output-param": {
                        "bind_ip": "default",
                        "drop_threshold_ms": 700,
                        "max_shutdown_time_sec": 30,
                        "pframe_drop_threshold_ms": 900
                    },
                    "protocol": "RTMP",
                    "service-param": {
                        "key": yt_key,
                        "server": "rtmp://a.rtmp.youtube.com/live2",
                    },
                }
            ],
            "video_configs": []
        }
        os.makedirs(os.path.dirname(OBS_OUTPUT_FILE), exist_ok=True)
        with open(OBS_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=4)
        log("YouTube stream key written to outputs.json")

    def write_facebook_service(self, fb_key):
        settings = {
            "settings": {
                "server": "rtmps://live-api-s.facebook.com:443/rtmp/",
                "key": fb_key
            },
            "type": "rtmp_custom",
            "service": "Facebook"
        }
        os.makedirs(os.path.dirname(OBS_SERVICE_FILE), exist_ok=True)
        with open(OBS_SERVICE_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        log("Facebook stream key written to service.json")

    def configure_obs_sources(self):
        selected_camera = self.camera_combo.get()
        selected_microphone = self.microphone_combo.get()
        config_file = "obs_device_config.json"
        config = {
            "video_device": selected_camera,
            "audio_device": selected_microphone
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        log(f"OBS configured with camera: {selected_camera}, mic: {selected_microphone}")

    def save_keys(self, yt_key, fb_key):
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump({"youtube": yt_key, "facebook": fb_key}, f, indent=4)

    def load_keys(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                keys = json.load(f)
                self.yt_entry.insert(0, keys.get("youtube", ""))
                self.fb_entry.insert(0, keys.get("facebook", ""))

    def update_timer(self):
        if self.streaming_start_time:
            elapsed = int(time.time() - self.streaming_start_time)
            hrs, rem = divmod(elapsed, 3600)
            mins, secs = divmod(rem, 60)
            self.timer_label.configure(text=f"{hrs:02}:{mins:02}:{secs:02}")
            self.after(1000, self.update_timer)


