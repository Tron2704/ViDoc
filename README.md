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
