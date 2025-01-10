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


def update_transcription(transcription):
    root.after(0, lambda: transcription_text.insert(tk.END, transcription + "\n"))


def start_recording():
    """
    Start recording audio. This function is triggered when the Record button is clicked.
    """
    global recording_thread, is_recording
    if not is_recording:  # Prevent multiple threads
        is_recording = True
        wave_label.config(text="Detecting sound waves...")
        transcriber.update_callback = update_transcription
        recording_thread = threading.Thread(target=transcriber.record_audio)
        recording_thread.start()


def stop_recording():
    """
    Stop recording audio, process chunks, and display the aggregated transcription.
    """
    global is_recording
    if is_recording:
        transcriber.stop_recording()  # Stops recording and processes remaining chunks
        is_recording = False
        wave_label.config(text="Waiting for sound waves...")
        try:
            transcription_text.delete("1.0", tk.END)
            transcription_text.insert(tk.END, "Transcription complete! Check console.")
        except Exception as e:
            transcription_text.delete("1.0", tk.END)
            transcription_text.insert(tk.END, f"Error: {e}")



# def stop_recording():
#     """
#     Stop recording audio, save it, and transcribe the recording.
#     This function is triggered when the Stop button is clicked.
#     """
#     global recording_thread, is_recording
#     if is_recording:
#         recording_thread.join()  # Wait for recording to finish
#         is_recording = False
#         wave_label.config(text="Waiting for sound waves...")
#         try:
#             transcriber.save_recording()  # Save the audio file
#             transcription = transcriber.transcribe()  # Perform transcription
#             transcription_text.delete("1.0", tk.END)
#             transcription_text.insert(tk.END, transcription)
#         except Exception as e:
#             transcription_text.delete("1.0", tk.END)
#             transcription_text.insert(tk.END, f"Error during transcription: {e}")



# Buttons
record_button = ttk.Button(button_frame, text="Record", command=start_recording)
stop_button = ttk.Button(button_frame, text="Stop", command=stop_recording)
record_button.pack(side="left", padx=10, pady=10)
stop_button.pack(side="left", padx=10, pady=10)


# Run Tkinter main loop
root.mainloop()
