import librosa
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import torch
from transformers import pipeline


class WhisperTransc:
    def __init__(self, model_name="openai/whisper-small"):
        self.fs = 44100
        self.chunk_duration = 10  # seconds
        self.chunk_size = self.fs * self.chunk_duration
        self.recording = []
        self.is_recording = False

        # Initialize the Whisper pipeline with chunking enabled
        self.pipeline = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            chunk_length_s=self.chunk_duration,
            return_timestamps=True,
            device=0 if torch.cuda.is_available() else -1,
        )

    def record_audio(self):
        """
        Start recording audio until `stop_recording` is called.
        """
        print("Recording...")
        self.is_recording = True
        self.recording = []
        with sd.InputStream(
            samplerate=self.fs,
            channels=1,
            callback=self.audio_callback,
            dtype="float32",
        ):
            while self.is_recording:
                sd.sleep(100)
        print("Recording completed!")

    def audio_callback(self, indata, frames, time, status):
        """
        Callback to append recorded audio data to `self.recording`.
        """
        if self.is_recording:
            self.recording.append(indata.copy())
            if len(self.recording) * len(indata) >= self.chunk_size:
                self.process_chunk()

    def process_chunk(self):
        """
        Process a completed audio chunk for transcription.
        """
        if len(self.recording) * len(self.recording[0]) < self.chunk_size:
            print("Not enough data for a full chunk. Skipping...")
            return

        audio_data = np.concatenate(self.recording[: self.chunk_size], axis=0)
        self.recording = self.recording[self.chunk_size :]
        print("Processing chunk for transcription...")
        transcription = self.transcribe_audio(audio_data)

        if hasattr(self, "update_callback"):
            self.update_callback(transcription)

    def stop_recording(self):
        """
        Stop recording audio.
        """
        self.is_recording = False
        if self.recording:
            print("Processing remaining audio...")
            remaining_audio = np.concatenate(self.recording, axis=0)
            transcription = self.transcribe_audio(remaining_audio)
            print(f"Remaining transcription: {transcription}")
            if hasattr(self, "update_callback"):
                self.update_callback(transcription)

    def transcribe_audio(self, audio_data):
        """
        Transcribe a given audio data array using the Whisper pipeline.
        """
        wav.write("Recording.wav", self.fs, (audio_data * 32767).astype(np.int16))
        audio_input, _ = librosa.load("Recording.wav", sr=16000)
        return self.pipeline(audio_input)["text"]