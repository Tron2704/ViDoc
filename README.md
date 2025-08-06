# 🎬 ViDoc – Video Info & Converter

A modern **FFmpeg GUI tool** built with Python & Tkinter that lets you:
- Inspect detailed media info for any video
- Select and keep specific streams (video/audio/subtitles)
- Re-encode or copy streams
- Change video codec, resolution, bit depth, and presets
- Re-encode audio with your chosen codec, channels, and bitrate
- Convert videos into MP4, MKV, or WebM formats with ease

---

## 🚀 Features

- 📜 **Detailed media info** using `ffprobe`
- 🎯 **Stream selection** (keep/remove specific streams)
- 🎥 **Video conversion** with codec, resolution, and pixel format options
- 🎵 **Audio re-encoding** with codec, channels, and bitrate settings
- 💾 Supports **MP4**, **MKV**, and **WebM** output containers
- ⚡ **FFmpeg-powered** for speed and quality
- 🚫 Built-in **codec–container compatibility validation**
- ⏳ Real-time **conversion progress bar**
- ❌ Cancel conversion at any time

---

## 🛠 Requirements

- **Python 3.8+**
- **FFmpeg** (must include `ffmpeg` and `ffprobe` in PATH)

### Python dependencies:
```bash
pip install tkinter
```
---

## 📦 Setup FFmpeg
Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/

Extract the ZIP file.

Copy the full path of the bin folder (e.g., C:\ffmpeg\bin)

Add it to your system Environment Variables → Path

### Test installation in a terminal:
```bash
ffmpeg -version
ffprobe -version
If you see version info for both, FFmpeg is correctly installed.
```
---

## 🚀 How to Run ViDoc

### Clone the repository:
```bash
git clone https://github.com/your-username/ViDoc.git
cd ViDoc
```
### Run the app:
```bash
python vidoc.py
```
---

## 📖 Usage Guide
1. Browse for a video file.
2. Review the detailed media info in the left pane.
3. Select which streams to keep/remove.
4. (Optional) For audio streams:
- Enable Re-encode audio
- Choose codec, channels, and bitrate
5. Choose:
- Output container (MP4/MKV/WebM)
- Video codec
- Resolution
- Bit depth
- Encoding preset
6. Click Convert to start conversion.
7. Monitor the progress bar & log output.

  ---

## ⚠️ Codec–Container Compatibility
ViDoc prevents you from choosing invalid codec–container combinations that FFmpeg can’t mux properly, e.g.:
❌ MP4 + VP9/AV1 video codec
❌ WebM + H.264/H.265 video codec
❌ WebM + AC3 audio codec

If you try to use an invalid combination, ViDoc will show an error before starting conversion.

---

## 💡 Tips
For lossless stream copy, set codec to Copy.
MKV container is the most flexible for unusual codec combinations.
For fastest conversion with minimal quality loss, use -c:v copy -c:a copy.
Use preset=ultrafast for fastest encoding speed (larger file size).
Use preset=veryslow for best compression (smaller file size, longer time).

---

## 🧩 Contributions

Want to improve ViDoc?

Fork this repo

Create a new branch (feature-name)

Commit your changes

Submit a pull request

--- 

## 📩 Issues & Feedback

If you find bugs or have suggestions:

Open a GitHub issue

Describe the problem & steps to reproduce

---

## 📜 License


This project is open-source under the MIT License.

---

## 🙌 Acknowledgements

FFmpeg
Tkinter

