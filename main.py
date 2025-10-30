import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import ImageGrab
import threading
import time

class ScreenRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        self.selection = None
        self.recording = False
        self.video_writer = None
        self.record_mode = None
        self.audio_enabled = tk.BooleanVar(value=False)
        self.audio_stream = None
        self.quality = tk.StringVar(value="720p")
        
        tk.Label(root, text="Screen Recorder", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Button(root, text="Record Full Screen", command=self.record_full_screen, width=30, bg="lightblue", height=2).pack(pady=10)
        
        tk.Button(root, text="Select Screen Area", command=self.select_area, width=30, bg="lightyellow", height=2).pack(pady=10)
        
        self.status_label = tk.Label(root, text="Ready", font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=5)
        
        tk.Checkbutton(root, text="Record PC Audio", variable=self.audio_enabled, font=("Arial", 10)).pack(pady=5)
        
        quality_frame = tk.Frame(root)
        quality_frame.pack(pady=5)
        tk.Label(quality_frame, text="Quality:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(quality_frame, text="480p", variable=self.quality, value="480p").pack(side=tk.LEFT)
        tk.Radiobutton(quality_frame, text="720p", variable=self.quality, value="720p").pack(side=tk.LEFT)
        tk.Radiobutton(quality_frame, text="1080p", variable=self.quality, value="1080p").pack(side=tk.LEFT)
        
        tk.Button(root, text="Start Recording", command=self.start_recording, width=30, bg="lightgreen", height=2).pack(pady=10)
        
        tk.Button(root, text="Stop Recording", command=self.stop_recording, width=30, bg="lightcoral", height=2).pack(pady=10)
        
        tk.Label(root, text="Video saved as: screen_record.mp4", font=("Arial", 9), fg="gray").pack(pady=5)
    
    def record_full_screen(self):
        screen = ImageGrab.grab()
        self.selection = (0, 0, screen.width, screen.height)
        self.record_mode = "full"
        self.status_label.config(text=f"Full Screen: {screen.width}x{screen.height} px", fg="green")
        messagebox.showinfo("Info", f"Full screen selected: {screen.width}x{screen.height} pixels")
    
    def select_area(self):
        self.record_mode = "select"
        self.root.withdraw()
        selector = AreaSelector(self.root, self.set_selection)
    
    def set_selection(self, x1, y1, x2, y2):
        self.selection = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        self.status_label.config(text=f"Area selected: {self.selection[2]-self.selection[0]}x{self.selection[3]-self.selection[1]} px", fg="green")
        self.root.deiconify()
    
    def start_recording(self):
        if not self.selection:
            messagebox.showerror("Error", "Please select an area or full screen first!")
            return
        
        if self.recording:
            messagebox.showwarning("Warning", "Already recording!")
            return
        
        self.recording = True
        if self.audio_enabled.get():
            messagebox.showwarning("Warning", "Audio device not found. Recording video only.")
            self.audio_enabled.set(False)
        threading.Thread(target=self._record, daemon=True).start()
        self.status_label.config(text="Recording...", fg="red")
    
    def _record(self):
        x1, y1, x2, y2 = self.selection
        width = x2 - x1
        height = y2 - y1
        
        quality = self.quality.get()
        scale_width, scale_height = self.get_quality_dimensions(width, height, quality)
        
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter("screen_record.mp4", fourcc, 20.0, (scale_width, scale_height))
        
        audio_thread = None
        if self.audio_enabled.get():
            audio_thread = threading.Thread(target=self._record_audio, daemon=True)
            audio_thread.start()
        
        while self.recording:
            try:
                screenshot = ImageGrab.grab(bbox=self.selection)
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                resized_frame = cv2.resize(frame, (scale_width, scale_height))
                self.video_writer.write(resized_frame)
            except Exception as e:
                print(f"Error: {e}")
                break
        
        if audio_thread:
            audio_thread.join(timeout=2)
    
    def get_quality_dimensions(self, width, height, quality):
        aspect_ratio = width / height
        if quality == "480p":
            target_height = 480
        elif quality == "720p":
            target_height = 720
        elif quality == "1080p":
            target_height = 1080
        else:
            target_height = 720
        
        target_width = int(target_height * aspect_ratio)
        if target_width % 2 != 0:
            target_width -= 1
        if target_height % 2 != 0:
            target_height -= 1
        
        return target_width, target_height
    
    def _record_audio(self):
        try:
            import pyaudio
            import wave
            
            p = pyaudio.PyAudio()
            
            device_index = None
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['max_input_channels'] > 0:
                    device_index = i
                    break
            
            if device_index is None:
                print("No audio input device found. Recording video only.")
                p.terminate()
                return
            
            samplerate = 44100
            channels = 2
            chunk = 2048
            
            stream = p.open(format=pyaudio.paFloat32, channels=channels, rate=samplerate, input=True, input_device_index=device_index, frames_per_buffer=chunk)
            
            frames = []
            while self.recording:
                try:
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Stream read error: {e}")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if frames:
                with wave.open("temp_audio.wav", 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(p.get_sample_size(pyaudio.paFloat32))
                    wf.setframerate(samplerate)
                    wf.writeframes(b''.join(frames))
        except Exception as e:
            print(f"Audio recording error: {e}")
    
    def stop_recording(self):
        if not self.recording:
            messagebox.showwarning("Warning", "Not recording!")
            return
        
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
        self.status_label.config(text="Ready", fg="blue")
        messagebox.showinfo("Info", "Recording saved as screen_record.mp4")


class AreaSelector:
    def __init__(self, parent, callback):
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.selector = tk.Toplevel(parent)
        self.selector.attributes('-fullscreen', True)
        self.selector.attributes('-alpha', 0.3)
        
        self.canvas = tk.Canvas(self.selector, bg="gray", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.create_text(50, 50, text="Click and drag to select area. Press ESC to cancel.", font=("Arial", 14), fill="white", anchor="nw")
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Escape>", lambda e: self.selector.destroy())
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)
    
    def on_release(self, event):
        self.callback(self.start_x, self.start_y, event.x, event.y)
        self.selector.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.mainloop()