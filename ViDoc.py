import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fractions import Fraction
import threading
import signal

available_streams = []
stream_keep_vars = {}
audio_reencode_vars = {}
audio_codec_vars = {}
audio_channels_vars = {}
audio_bitrate_vars = {}
input_file_path = ""
ffmpeg_process = None

# ---------- Helpers ----------
def format_duration(seconds):
    try:
        seconds = float(seconds)
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"
    except:
        return "N/A"

def format_size(bytes_size):
    if not bytes_size:
        return "N/A"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024**2:
        return f"{bytes_size/1024:.2f} KB"
    elif bytes_size < 1024**3:
        return f"{bytes_size/(1024**2):.2f} MB"
    else:
        return f"{bytes_size/(1024**3):.2f} GB"

def parse_fps(fps_value):
    try:
        if "/" in fps_value:
            return round(float(Fraction(fps_value)), 2)
        return float(fps_value)
    except:
        return fps_value

# ---------- Browse File ----------
def browse_file():
    global input_file_path
    input_file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov *.flv *.ts *.webm"), ("All files", "*.*")]
    )
    if input_file_path:
        filename_entry.delete(0, tk.END)
        filename_entry.insert(0, input_file_path)
        show_media_info(input_file_path)

# ---------- Get Media Info ----------
def show_media_info(file_path):
    global stream_keep_vars, audio_reencode_vars, audio_codec_vars, audio_channels_vars, audio_bitrate_vars
    stream_keep_vars = {}
    audio_reencode_vars = {}
    audio_codec_vars = {}
    audio_channels_vars = {}
    audio_bitrate_vars = {}
    clear_info_section()

    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)

        duration = info.get("format", {}).get("duration", "N/A")
        bit_rate = info.get("format", {}).get("bit_rate", "N/A")
        file_size = os.path.getsize(file_path)

        tk.Label(info_frame_scroll, text=f"Total File Size: {format_size(file_size)}",
                 font=("Courier New", 12), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=8, padx=10)
        tk.Label(info_frame_scroll, text=f"Total Duration: {format_duration(duration)}",
                 font=("Courier New", 12), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=8, padx=10)
        if bit_rate != "N/A":
            tk.Label(info_frame_scroll, text=f"Overall Bitrate: {int(bit_rate)//1000} kbps",
                     font=("Courier New", 12), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=8, padx=10)

        tk.Label(info_frame_scroll, text="-"*50, font=("Courier New", 10),
                 fg="#00ffcc", bg="#121212").pack(fill="x", pady=15, padx=10)

        for i, stream in enumerate(info.get("streams", [])):
            codec_type = stream.get("codec_type", "unknown").capitalize()
            codec_name = stream.get("codec_name", "N/A")
            lang = stream.get("tags", {}).get("language", "und")
            duration_s = stream.get("duration", duration)
            bitrate_s = stream.get("bit_rate", None) or stream.get("tags", {}).get("BPS", None)

            section = tk.Frame(info_frame_scroll, relief=tk.SOLID, bd=1, bg="#212121", padx=10, pady=10)
            section.pack(fill="x", pady=5, padx=10)

            # Fix stream ID format - use the actual stream index
            stream_index = stream.get('index', i)
            stream_id = f"{stream.get('codec_type')[0]}:{stream_index}"
            var = tk.BooleanVar(value=True)
            stream_keep_vars[stream_id] = var

            tk.Label(section, text=f"Stream #{stream_index} - {codec_type}",
                     font=("Courier New", 12, "bold"), fg="#00ffcc", bg="#212121").pack(anchor="w", pady=5)
            tk.Label(section, text=f"Codec: {codec_name}",
                     font=("Courier New", 12), fg="#00ffcc", bg="#212121").pack(anchor="w", pady=5)
            tk.Label(section, text=f"Language: {lang}",
                     font=("Courier New", 12), fg="#00ffcc", bg="#212121").pack(anchor="w", pady=5)
            tk.Label(section, text=f"Duration: {format_duration(duration_s)}",
                     font=("Courier New", 12), fg="#00ffcc", bg="#212121").pack(anchor="w", pady=5)
            if bitrate_s:
                tk.Label(section, text=f"Bitrate: {int(bitrate_s)//1000} kbps",
                         font=("Courier New", 12), fg="#00ffcc", bg="#212121").pack(anchor="w", pady=5)

            if codec_type == "Video":
                width = stream.get("width", "N/A")
                height = stream.get("height", "N/A")
                fps = parse_fps(stream.get("avg_frame_rate", "N/A"))
                tk.Label(section, text=f"Resolution: {width}x{height}",
                         font=("Courier New", 12), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5)
                tk.Label(section, text=f"FPS: {fps}",
                         font=("Courier New", 12), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5)

            tk.Checkbutton(section, text=f"Keep this stream",
                           variable=var, font=("Courier New", 11),
                           fg="#00ffcc", bg="#212121", selectcolor="#121212").pack(anchor="w")

            # Extra options for Audio streams
            if codec_type == "Audio":
                re_var = tk.BooleanVar(value=False)
                audio_reencode_vars[stream_id] = re_var
                tk.Checkbutton(section, text="Re-encode this audio",
                               variable=re_var, font=("Courier New", 11),
                               fg="#ffaa00", bg="#212121", selectcolor="#121212").pack(anchor="w", pady=(5, 0))

                # Audio codec (radio buttons)
                tk.Label(section, text="Codec:", font=("Courier New", 10), fg="#ffaa00", bg="#212121").pack(anchor="w")
                codec_opt = tk.StringVar(value="aac")
                audio_codec_vars[stream_id] = codec_opt
                for codec in ["aac", "libopus", "libmp3lame", "ac3", "flac", "eac3", "mp2"]:
                    tk.Radiobutton(
                        section, text=codec, variable=codec_opt, value=codec,
                        font=("Courier New", 10), fg="#ffaa00", bg="#212121",
                        selectcolor="#121212", activebackground="#212121"
                    ).pack(anchor="w", padx=20)

                # Channels (radio buttons)
                tk.Label(section, text="Channels:", font=("Courier New", 10), fg="#ffaa00", bg="#212121").pack(anchor="w")
                ch_opt = tk.StringVar(value="2")
                audio_channels_vars[stream_id] = ch_opt
                for ch in ["1", "2", "6"]:
                    tk.Radiobutton(
                        section, text=ch, variable=ch_opt, value=ch,
                        font=("Courier New", 10), fg="#ffaa00", bg="#212121",
                        selectcolor="#121212", activebackground="#212121"
                    ).pack(anchor="w", padx=20)

                # Bitrate (radio buttons)
                tk.Label(section, text="Bitrate:", font=("Courier New", 10), fg="#ffaa00", bg="#212121").pack(anchor="w")
                br_opt = tk.StringVar(value="128k")
                audio_bitrate_vars[stream_id] = br_opt
                for br in ["96k", "128k", "256k", "320k", "384k", "448k", "640k", "768k"]:
                    tk.Radiobutton(
                        section, text=br, variable=br_opt, value=br,
                        font=("Courier New", 10), fg="#ffaa00", bg="#212121",
                        selectcolor="#121212", activebackground="#212121"
                    ).pack(anchor="w", padx=20)



    except Exception as e:
        messagebox.showerror("Error", f"Failed to get media info: {e}")

# ---------- Clear Info ----------
def clear_info_section():
    for widget in info_frame_scroll.winfo_children():
        widget.destroy()

# ---------- Cancel ----------
def cancel_conversion():
    global ffmpeg_process
    if ffmpeg_process and ffmpeg_process.poll() is None:
        ffmpeg_process.terminate()
        log_text.insert(tk.END, "\nConversion cancelled by user.\n")
        log_text.see(tk.END)
        progress_bar['value'] = 0


# ---------- Convert ----------
def convert_video():
    global input_file_path, ffmpeg_process

    # Step 1: Validate input file
    if not input_file_path:
        messagebox.showerror("Error", "Please select an input file first.")
        return

    # Step 2: Output file dialog and validation
    output_ext = output_format_var.get()
    output_path = filedialog.asksaveasfilename(
        defaultextension=f".{output_ext}",
        filetypes=[(output_ext.upper(), f"*.{output_ext}"), ("All Files", "*.*")]
    )
    if not output_path:
        return

    # Step 3: Get user selections for codec, resolution, preset, and pix_fmt
    chosen_codec = codec_var.get()
    chosen_res = resolution_var.get()
    chosen_preset = preset_var.get()
    chosen_pix_fmt = bitdepth_var.get()

    # Step 3.5: Validate codec-container compatibility
    invalid_combinations = {
        "mp4": ["libvpx-vp9", "libaom-av1"],   # MP4 doesn't support VP9/AV1 well for playback
        "webm": ["libx264", "libx265", "ac3"], # WEBM typically uses VP8/VP9/AV1 + opus/vorbis
        "mkv": []                              # MKV is flexible
    }
    if chosen_codec in invalid_combinations.get(output_ext, []):
        messagebox.showerror(
            "Invalid Combination",
            f"The selected codec '{chosen_codec}' is not recommended/compatible with .{output_ext} container.\n"
            "Please choose a compatible codec."
        )
        return

    # Step 4: Initialize the FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", input_file_path]

    # Step 5: Map streams and handle audio re-encoding
    audio_stream_count = 0
    video_stream_count = 0
    
    for sid, var in stream_keep_vars.items():
        if var.get():  # Stream is kept
            # Extract the actual stream index from the stream ID
            stream_index = sid.split(':')[1]
            cmd += ["-map", f"0:{stream_index}"]

            # Handle audio streams
            if sid.startswith("a:"):  # Audio stream
                if audio_reencode_vars.get(sid, tk.BooleanVar()).get():  # If audio re-encode is selected
                    codec = audio_codec_vars[sid].get()
                    bitrate = audio_bitrate_vars[sid].get()
                    channels = audio_channels_vars[sid].get()
                    
                    # Use the output stream index for codec assignment
                    cmd += [f"-c:a:{audio_stream_count}", codec]
                    cmd += [f"-b:a:{audio_stream_count}", bitrate]
                    cmd += [f"-ac:{audio_stream_count}", channels]
                else:
                    cmd += [f"-c:a:{audio_stream_count}", "copy"]
                
                audio_stream_count += 1
            
            elif sid.startswith("v:"):  # Video stream
                video_stream_count += 1

    # Step 6: Video codec settings
    cmd += ["-c:v", chosen_codec]
    if chosen_codec != "copy" and chosen_pix_fmt != "same":
        cmd += ["-pix_fmt", chosen_pix_fmt]

    # Preset for video codec (if selected)
    valid_presets = [
        "ultrafast", "superfast", "veryfast", "faster", "fast",
        "medium", "slow", "slower", "veryslow", "placebo"
    ]
    if chosen_codec != "copy" and chosen_preset in valid_presets:
        cmd += ["-preset", chosen_preset]

    # Resolution settings (if changed from default)
    if chosen_res != "same" and chosen_codec != "copy":
        w, h = chosen_res.split(":")
        cmd += ["-vf", f"scale={w}:{h}"]

    # Step 7: Subtitle handling (just copy subtitles)
    cmd += ["-c:s", "copy", output_path]

    # Step 8: Reset progress bar and log text
    progress_bar['value'] = 0
    log_text.delete(1.0, tk.END)
    
    # Debug: Print the command to log
    log_text.insert(tk.END, f"FFmpeg command: {' '.join(cmd)}\n\n")
    log_text.see(tk.END)

    # Step 9: Define a function to run FFmpeg with real-time progress updates
    def run():
        global ffmpeg_process
        try:
            # Get video duration for progress calculation
            total_duration = get_video_duration(input_file_path)

            # Start FFmpeg process
            ffmpeg_process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, universal_newlines=True)
            for line in ffmpeg_process.stderr:
                log_text.insert(tk.END, line)
                log_text.see(tk.END)
                
                # Extract timestamp from ffmpeg stderr output to calculate progress
                if "time=" in line:
                    timestamp = line.split("time=")[-1].split(" ")[0]
                    current_time = parse_time_to_seconds(timestamp)
                    if total_duration > 0:
                        percent = (current_time / total_duration) * 100
                        progress_bar['value'] = percent

            # Wait for the FFmpeg process to finish
            ffmpeg_process.wait()

            # Check the result of the conversion
            if ffmpeg_process.returncode == 0:
                messagebox.showinfo("Success", f"Conversion completed:\n{output_path}")
            elif ffmpeg_process.returncode != -15:
                messagebox.showerror("Error", f"Conversion failed.\nSee log for details.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    # Step 10: Use threading to run the conversion in the background
    threading.Thread(target=run, daemon=True).start()

def get_video_duration(path):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def parse_time_to_seconds(time_str):
    try:
        h, m, s = time_str.split(":")
        s = float(s)
        return int(h) * 3600 + int(m) * 60 + s
    except:
        return 0

# ---------- GUI ----------
root = tk.Tk()
root.title("Video Info & Converter")
root.geometry("1280x900")
root.config(bg="#121212")

style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", thickness=20, troughcolor='#212121', background='#00ffcc')
style.configure("Custom.Vertical.TScrollbar", background="#00ffcc", troughcolor="#212121", width=15)

# Top input
top_frame = tk.Frame(root, bg="#121212")
top_frame.pack(fill="x", pady=10)
filename_entry = tk.Entry(top_frame, width=70, font=("Courier New", 12),
                          relief="flat", bd=1, bg="#121212", fg="#00ffcc", insertbackground="#00ffcc")
filename_entry.pack(side="left", padx=5, fill="x", expand=True)
tk.Button(top_frame, text="Browse", command=browse_file,
          font=("Courier New", 12), bg="#00ffcc", fg="black",
          relief="flat", padx=20, pady=8).pack(side="left", padx=10)

# Panes
main_pane = tk.PanedWindow(root, orient="horizontal", bg="#121212", sashwidth=4, sashrelief="raised")
main_pane.pack(fill="both", expand=True, padx=5)

# Left
left_frame = tk.Frame(main_pane, bg="#121212")
left_canvas = tk.Canvas(left_frame, bg="#121212", highlightthickness=0)
left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview, style="Custom.Vertical.TScrollbar")
info_frame_scroll = tk.Frame(left_canvas, bg="#121212")
info_frame_scroll.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
left_canvas.create_window((0, 0), window=info_frame_scroll, anchor="nw", width=580)
left_canvas.configure(yscrollcommand=left_scrollbar.set)
main_pane.add(left_frame, minsize=600)
left_canvas.pack(side="left", fill="both", expand=True)
left_scrollbar.pack(side="right", fill="y")

# Right
right_frame = tk.Frame(main_pane, bg="#121212")
right_canvas = tk.Canvas(right_frame, bg="#121212", highlightthickness=0)
right_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview, style="Custom.Vertical.TScrollbar")
convert_frame = tk.Frame(right_canvas, bg="#121212")
convert_frame.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
right_canvas.create_window((0, 0), window=convert_frame, anchor="nw", width=580)
right_canvas.configure(yscrollcommand=right_scrollbar.set)
main_pane.add(right_frame, minsize=600)
right_canvas.pack(side="left", fill="both", expand=True)
right_scrollbar.pack(side="right", fill="y")

# Controls
tk.Label(convert_frame, text="Convert Video To:", font=("Courier New", 12, "bold"), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5, padx=10)
output_format_var = tk.StringVar(value="mp4")
formats = [("MP4", "mp4"), ("MKV", "mkv"), ("WEBM", "webm")]
fmt_frame = tk.Frame(convert_frame, bg="#121212"); fmt_frame.pack(anchor="w", padx=10)
for i, (text, value) in enumerate(formats):
    tk.Radiobutton(fmt_frame, text=text, variable=output_format_var, value=value,
                   font=("Courier New", 12), fg="#00ffcc", bg="#121212",
                   selectcolor="#121212").grid(row=i//5, column=i%5, padx=5, pady=3, sticky="w")

tk.Label(convert_frame, text="Select Video Codec:", font=("Courier New", 12, "bold"), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5, padx=10)
codec_var = tk.StringVar(value="libx264")
codecs = [("H.264", "libx264"), ("HEVC (H.265)", "libx265"), ("VP9", "libvpx-vp9"), ("AV1", "libaom-av1"), ("Copy", "copy")]
codec_frame = tk.Frame(convert_frame, bg="#121212"); codec_frame.pack(anchor="w", padx=10)
for i, (text, value) in enumerate(codecs):
    tk.Radiobutton(codec_frame, text=text, variable=codec_var, value=value,
                   font=("Courier New", 12), fg="#00ffcc", bg="#121212",
                   selectcolor="#121212").grid(row=i//5, column=i%5, padx=5, pady=3, sticky="w")

tk.Label(convert_frame, text="Select Resolution:", font=("Courier New", 12, "bold"), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5, padx=10)
resolution_var = tk.StringVar(value="same")
resolutions = {
    "144p": (256, 144), "240p": (426, 240), "360p": (640, 360),
    "480p (SD)": (854, 480), "540p": (960, 540), "720p (HD)": (1280, 720),
    "900p (HD)": (1600, 900), "1080p (FHD)": (1920, 1080),
    "1440p (2K)": (2560, 1440), "2160p (4K)": (3840, 2160)
}
res_options = [("Same as Original", "same")] + [(label, f"{w}:{h}") for label, (w, h) in resolutions.items()]
res_frame = tk.Frame(convert_frame, bg="#121212"); res_frame.pack(anchor="w", padx=10)
for i, (label, val) in enumerate(res_options):
    tk.Radiobutton(res_frame, text=label, variable=resolution_var, value=val,
                   font=("Courier New", 12), fg="#00ffcc", bg="#121212",
                   selectcolor="#121212").grid(row=i//4, column=i%4, padx=5, pady=3,sticky="w")

tk.Label(convert_frame, text="Select Bit Depth:", font=("Courier New", 12, "bold"), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5, padx=10)
bitdepth_var = tk.StringVar(value="same")
bitdepths = [("Same as Original", "same"), ("8-bit", "yuv420p"), ("10-bit", "yuv420p10le"), ("12-bit", "yuv420p12le")]
bit_frame = tk.Frame(convert_frame, bg="#121212"); bit_frame.pack(anchor="w", padx=10)
for i, (text, val) in enumerate(bitdepths):
    tk.Radiobutton(bit_frame, text=text, variable=bitdepth_var, value=val,
                   font=("Courier New", 12), fg="#00ffcc", bg="#121212",
                   selectcolor="#121212").grid(row=i//2, column=i%2, padx=5, pady=3, sticky="w")

tk.Label(convert_frame, text="Select Preset:", font=("Courier New", 12, "bold"), fg="#00ffcc", bg="#121212").pack(anchor="w", pady=5, padx=10)
preset_var = tk.StringVar(value="default")
presets = [("Default", "default"), ("Ultrafast", "ultrafast"), ("Superfast", "superfast"),
           ("Veryfast", "veryfast"), ("Faster", "faster"), ("Fast", "fast"),
           ("Medium", "medium"), ("Slow", "slow"), ("Slower", "slower"), ("Veryslow", "veryslow")]
preset_frame = tk.Frame(convert_frame, bg="#121212"); preset_frame.pack(anchor="w", padx=10)
for i, (text, val) in enumerate(presets):
    tk.Radiobutton(preset_frame, text=text, variable=preset_var, value=val,
                   font=("Courier New", 12), fg="#00ffcc", bg="#121212",
                   selectcolor="#121212").grid(row=i//4, column=i%4, padx=5, pady=3, sticky="w")

# Progress bar
progress_bar = ttk.Progressbar(convert_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10, padx=10)

# Log output
log_text = tk.Text(convert_frame, height=10, bg="#1e1e1e", fg="#00ffcc", font=("Courier New", 10))
log_text.pack(fill="x", padx=10, pady=5)

# Convert & Cancel buttons
btn_frame = tk.Frame(convert_frame, bg="#121212")
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Convert", command=convert_video,
          font=("Courier New", 14, "bold"), bg="#00ffcc", fg="black", relief="flat",
          padx=20, pady=10).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Cancel", command=cancel_conversion,
          font=("Courier New", 14, "bold"), bg="#ff4444", fg="white", relief="flat",
          padx=20, pady=10).grid(row=0, column=1, padx=5)

root.mainloop()
