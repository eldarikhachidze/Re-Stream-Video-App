# Multi Stream Manager

This Python application allows you to stream to multiple platforms (e.g., YouTube, Facebook) simultaneously using OBS Studio. The app features a clean and easy-to-use interface for entering stream keys, selecting devices, and managing streams.

## Features

- **Simultaneous Streaming:** Stream to multiple platforms at the same time (YouTube, Facebook).
- **Device Management:** Select and configure camera and microphone devices for OBS.
- **Stream Key Management:** Easily enter and save stream keys for YouTube and Facebook.
- **Test Mode:** Run the app in test mode to simulate streaming without actually launching OBS.
- **Logging:** All app activity is logged for easy troubleshooting and monitoring.

## Requirements

- Python 3.x
- OBS Studio
- ffmpeg (ensure ffmpeg is available in your system's PATH)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/multi-stream-manager.git
    cd multi-stream-manager
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Download **OBS Studio** from [here](https://obsproject.com/) and make sure it's installed properly.

4. **Download `ffmpeg.exe` and place it in the `bin` folder.**  
   You can get `ffmpeg` from [here](https://ffmpeg.org/download.html). After downloading, place the `ffmpeg.exe` binary in the `bin` directory of your project.

5. Run the application:
    ```bash
    python app.py
    ```

## Usage

1. **Enter Stream Keys:** Input your YouTube and Facebook stream keys in the respective fields.
2. **Select Devices:** Choose the microphone and camera you want to use for the stream.
3. **Start Streaming:** Click the "Start Streaming" button to begin streaming. OBS will automatically launch with your settings.

## Logging

All activities and errors are logged to the `stream_log.txt` file.

## Troubleshooting

- **OBS doesn't launch:** Ensure the OBS path is correctly configured in `main_window.py`.
- **Stream keys are not working:** Double-check your keys and make sure they are entered correctly.

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.
