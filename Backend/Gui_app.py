import threading
import tkinter as tk
from tkinter import ttk

from Whisper_transc import WhisperTransc

# Initialize WhisperTransc
transcriber = WhisperTransc()

# Tkinter root window
root = tk.Tk()
root.title("Speech Translation GUI")

# Frames
left_frame = tk.Frame(root, width=400, height=300, bg="white")
right_frame = tk.Frame(root, width=400, height=300, bg="lightgrey")
left_frame.pack(side="left", fill="both", expand=True)
right_frame.pack(side="right", fill="both", expand=True)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(side="bottom", fill="x")

# Left Window: Sound wave detection label
wave_label = tk.Label(
    left_frame, text="Waiting for sound waves...", font=("Arial", 14), bg="white"
)
wave_label.pack(expand=True)

# Right Window: Transcription text area
transcription_label = tk.Label(
    right_frame, text="Transcription Results", font=("Arial", 14), bg="lightgrey"
)
transcription_label.pack(pady=10)

transcription_text = tk.Text(right_frame, wrap="word", height=10, width=50)
transcription_text.pack(padx=10, pady=10)

# Global variables
recording_thread = None
is_recording = False
sound_file = "./Sound/notification-sound.wav"


def update_transcription(transcription):
    """
    Append the transcription to the transcription text area in real-time.
    """
    transcription_text.insert(tk.END, transcription + "\n")
    transcription_text.see(tk.END)  # Automatically scroll to the latest transcription


def start_recording_button():
    """
    Start recording audio. This function is triggered when the Record button is clicked.
    """
    try:
        transcriber.play_notification_sound(sound_file)
    except Exception as e:
        print(f"Error playing notification sound: {e}")

    global recording_thread, is_recording
    if not is_recording:  # Prevent multiple threads
        is_recording = True
        wave_label.config(text="Detecting sound waves...")
        transcription_text.delete("1.0", tk.END)
        transcriber.update_callback = update_transcription
        recording_thread = threading.Thread(target=transcriber.record_audio)
        recording_thread.start()


def stop_recording_button():
    """
    Stop recording audio, save it, and transcribe the recording.
    This function is triggered when the Stop button is clicked.
    """
    transcriber.play_notification_sound(sound_file)

    global is_recording
    if is_recording:
        is_recording = False
        transcriber.stop_recording()
        wave_label.config(text="Waiting for sound waves...")


# Buttons
record_button = ttk.Button(button_frame, text="Record", command=start_recording_button)
stop_button = ttk.Button(button_frame, text="Stop", command=stop_recording_button)
record_button.pack(side="left", padx=10, pady=10)
stop_button.pack(side="left", padx=10, pady=10)


# Run Tkinter main loop
root.mainloop()