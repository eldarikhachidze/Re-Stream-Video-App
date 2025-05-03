import customtkinter as ctk
from tkinter import messagebox
import subprocess, os, time, json, socket
from datetime import datetime

OBS_PATH = r"C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe"
OBS_OUTPUT_FILE = os.path.expanduser("~\\AppData\\Roaming\\obs-studio\\basic\\profiles\\Untitled\\obs-multi-rtmp.json")
OBS_SERVICE_FILE = os.path.expanduser("~\\AppData\\Roaming\\obs-studio\\basic\\profiles\\Untitled\\service.json")
KEY_FILE = "stream_keys.json"
LOG_FILE = "stream_log.txt"


class StreamApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔴 Multi Stream Manager")
        self.geometry("500x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.obs_process = None
        self.streaming_start_time = None
        self.test_mode = ctk.BooleanVar()

        self.create_widgets()
        self.load_keys()
        self.log("App started")

    def create_widgets(self):
        ctk.CTkLabel(self, text="YouTube Stream Key:").pack(pady=(20, 5))
        self.yt_entry = ctk.CTkEntry(self, width=400)
        self.yt_entry.pack()

        ctk.CTkLabel(self, text="Facebook Stream Key:").pack(pady=(20, 5))
        self.fb_entry = ctk.CTkEntry(self, width=400)
        self.fb_entry.pack()

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

    def check_internet(self):
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=2)
            return True
        except:
            return False

    def start_stream(self):
        yt_key = self.yt_entry.get().strip()
        fb_key = self.fb_entry.get().strip()

        if not yt_key or not fb_key:
            messagebox.showerror("Error", "Please enter both stream keys.")
            return

        if not self.check_internet():
            messagebox.showerror("Error", "No internet connection.")
            return

        self.save_keys(yt_key, fb_key)
        self.write_youtube_output(yt_key)
        self.write_facebook_service(fb_key)

        self.start_obs()

        self.streaming_start_time = time.time()
        self.update_timer()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Status: Streaming...", text_color="green")
        self.log("Streaming started")

    def stop_stream(self):
        if self.obs_process:
            self.obs_process.terminate()
            self.obs_process = None
        self.status_label.configure(text="Status: Stopped", text_color="red")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.log("Streaming stopped")
        messagebox.showinfo("Info", "Streaming stopped successfully.")

    def start_obs(self):
        if not os.path.exists(OBS_PATH):
            messagebox.showerror("Error", "OBS path not found.")
            return

        if self.test_mode.get():
            self.log("Test mode enabled, OBS will not start.")
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
                        "key": "asdasdasdas",
                        "server": "rtmp://a.rtmp.youtube.com/live2",
                    },
                }
            ],
            "video_configs": []
        }
        os.makedirs(os.path.dirname(OBS_OUTPUT_FILE), exist_ok=True)
        with open(OBS_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=4)
        self.log("YouTube stream key written to outputs.json")

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
        self.log("Facebook stream key written to service.json")

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

    def log(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {message}\n")


if __name__ == "__main__":
    app = StreamApp()
    app.mainloop()
