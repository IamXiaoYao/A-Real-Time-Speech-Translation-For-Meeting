import threading
import tkinter as tk
from tkinter import filedialog, ttk

from Whisper_transc import WhisperTransc

# Initialize WhisperTransc
transcriber = WhisperTransc()

# Tkinter root window
root = tk.Tk()
root.title("Real-time Speech Translation")

# Frames
left_frame = tk.Frame(root, width=400, height=300, bg="white")
right_frame = tk.Frame(root, width=400, height=300, bg="lightgrey")
left_frame.pack(side="left", fill="both", expand=True)
right_frame.pack(side="right", fill="both", expand=True)

# Buttons
button_frame = tk.Frame(left_frame, bg="white", height=40)
button_frame.pack(side="top", fill="x")

# Left Window: Sound wave detection label
wave_label = tk.Label(
    left_frame, text="Sound wave detection", font=("Arial", 14), bg="white"
)
wave_label.pack(pady=5)

Sound_wave_area = tk.Text(left_frame, wrap="word", width=50)
Sound_wave_area.pack(expand=True)

# Right Window: Transcription text area
transcription_label = tk.Label(
    right_frame, text="Transcription Results", font=("Arial", 14), bg="lightgrey"
)
transcription_label.pack(pady=10)

transcription_text = tk.Text(right_frame, wrap="word", width=50)
transcription_text.pack(expand=True)


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


def upload_recording_button():
    try:
        audio_file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.ogg")]
        )
        if not audio_file_path:
            return
        # Transcribe the uploaded audio file
        transcription = transcriber.transcribe(audio_file_path)

        # Display the transcription
        transcription_text.insert(tk.END, transcription + "\n")
        transcription_text.see(
            tk.END
        )  # Automatically scroll to the latest transcription

    except Exception as e:
        print(f"Error uploading or transcribing the file: {e}")


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
upload_button = ttk.Button(button_frame, text="Upload", command=upload_recording_button)
record_button = ttk.Button(button_frame, text="Record", command=start_recording_button)
stop_button = ttk.Button(button_frame, text="Stop", command=stop_recording_button)
upload_button.pack(side="left", padx=10, pady=10, expand=True)
record_button.pack(side="left", padx=10, pady=10, expand=True)
stop_button.pack(side="left", padx=10, pady=10, expand=True)


# Run Tkinter main loop
root.mainloop()