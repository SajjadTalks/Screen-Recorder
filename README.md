# 🎥 Screen Recorder App (Python + Tkinter)

A simple **desktop screen recorder** built with **Python**, **Tkinter**, **OpenCV**, and **Pillow**.  
It allows you to record **full screen** or **selected area**, choose **video quality (480p, 720p, 1080p)**, and optionally record **audio**.

---

## 🧩 Features

✅ Record **full screen** or **custom area**  
✅ Choose video quality: **480p**, **720p**, or **1080p**  
✅ Simple **GUI** built with Tkinter  
✅ Saves video as `screen_record.mp4`  
✅ Optional **audio recording** (via PyAudio)  
✅ Works on **Windows**, **macOS**, and **Linux**

---

## ⚙️ Requirements

Install dependencies using pip:

```bash
pip install -r requirements.txt
````

### `requirements.txt`

```
tkinter
opencv-python
numpy
Pillow
pyaudio
```

> 📝 Note:
>
> * `tkinter` is built-in with Python (no need to install manually on most systems).
> * On **Linux**, install additional tools:
>
>   ```bash
>   sudo apt install python3-tk scrot xclip portaudio19-dev
>   ```
> * Then reinstall PyAudio if needed:
>
>   ```bash
>   pip install pyaudio
>   ```

---

## ▶️ How to Use

1. **Clone the repository**

   ```bash
   git clone https://github.com/SajjadTalks/Screen-Recorder.git
   cd screen-recorder
   ```

2. **Run the app**

   ```bash
   python main.py
   ```

3. **Select what to record**

   * Click **Record Full Screen** to capture the entire screen
   * Or **Select Screen Area** to draw a rectangle and record that part only

4. **Adjust settings**

   * Choose video quality (**480p**, **720p**, or **1080p**)
   * (Optional) Enable **Record PC Audio**

5. **Start Recording**

   * Click **Start Recording** to begin
   * Click **Stop Recording** to end

6. The video will be saved automatically as:

   ```
   screen_record.mp4
   ```

---

## 📂 File Structure

```
screen-recorder/
├── main.py      # Main application
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🧠 How It Works

* The app uses **Pillow (ImageGrab)** to take screenshots repeatedly.
* Converts images to frames using **NumPy** and **OpenCV**.
* Writes frames to an MP4 file via **cv2.VideoWriter**.
* (Optional) Records system audio using **PyAudio**.
* The **Tkinter GUI** controls start, stop, and area selection.

---

## ⚠️ Known Issues

* Audio recording may not work on some systems (especially Linux without proper PulseAudio/ALSA setup).
* High resolutions (1080p+) may result in lower frame rates on older CPUs.

