import librosa
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import torch
from transformers import pipeline


class WhisperTransc:
    def __init__(self, model_name="openai/whisper-small"):
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.fs = 44100
        self.recording = None
    def record_audio(self, duration):
        print("Recording...")
        self.recording = sd.rec(
            int(duration * self.fs), samplerate=self.fs, channels=1, dtype="float32"
        )
        sd.wait()
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
