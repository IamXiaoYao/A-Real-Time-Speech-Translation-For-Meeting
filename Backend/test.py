import threading
from queue import Queue

import numpy as np
import sounddevice as sd
import torch
from playsound import playsound
from transformers import pipeline


class WhisperTransc:
    def __init__(self, model_name="openai/whisper-base.en"):
        # Whisper settings
        self.fs = 16000  # Whisper's native sample rate
        self.chunk_duration = 2  # seconds
        self.chunk_size = self.fs * self.chunk_duration
        self.overlap_duration = 0.5  # seconds
        self.overlap_size = self.fs * self.overlap_duration

        # Buffer and state
        self.audio_buffer = np.zeros(self.chunk_size, dtype=np.float32)
        self.queue = Queue()
        self.is_recording = False

        # Whisper pipeline
        self.pipeline = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            chunk_length_s=self.chunk_duration,
            return_timestamps=True,
            device=0 if torch.cuda.is_available() else -1,
        )

    def audio_callback(self, indata, frames, time, status):
        """
        Append audio to the buffer and push chunks to the queue.
        """
        if not self.is_recording:
            return

        # Shift the buffer and add new data
        self.audio_buffer = np.roll(self.audio_buffer, -frames)
        self.audio_buffer[-frames:] = indata.flatten()

        # If the buffer is full, enqueue a chunk for transcription
        if self.queue.qsize() < 5:  # Prevent overloading the queue
            chunk = self.audio_buffer[:]
            self.queue.put(chunk)

    def start_transcription_thread(self):
        """
        Background thread to process chunks for transcription.
        """

        def transcribe():
            while self.is_recording or not self.queue.empty():
                if not self.queue.empty():
                    chunk = self.queue.get()
                    transcription = self.transcribe_audio(chunk)
                    if hasattr(self, "update_callback"):
                        self.update_callback(transcription)

        threading.Thread(target=transcribe, daemon=True).start()

    def transcribe_audio(self, audio_data):
        """
        Transcribe a given audio chunk using the Whisper pipeline.
        """
        try:
            transcription = self.pipeline(audio_data)["text"]
            return transcription
        except Exception as e:
            print(f"Error during transcription: {e}")
            return "Transcription error occurred."

    def record_audio(self):
        """
        Start recording and transcription.
        """
        self.is_recording = True
        self.audio_buffer = np.zeros(self.chunk_size, dtype=np.float32)
        print("Recording started...")
        self.start_transcription_thread()

        with sd.InputStream(
            samplerate=self.fs,
            channels=1,
            dtype="float32",
            callback=self.audio_callback,
        ):
            while self.is_recording:
                sd.sleep(100)

    def stop_recording(self):
        """
        Stop recording and process remaining audio in the queue.
        """
        self.is_recording = False
        print("Stopping recording...")

    def play_notification_sound(self, sound_file):
        playsound(sound_file)


# def transcribe_audio(self, audio_data):
#     """
#     Transcribe a given audio data array using the Whisper pipeline.
#     """
#     wav.write("Recording.wav", self.fs, (audio_data * 32767).astype(np.int16))
#     audio_input, _ = librosa.load("Recording.wav", sr=16000)
#     return self.pipeline(audio_input)["text"]
