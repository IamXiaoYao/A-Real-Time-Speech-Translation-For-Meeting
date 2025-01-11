import librosa
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import torch
from playsound import playsound
from transformers import pipeline


class WhisperTransc:
    def __init__(self, model_name="openai/whisper-small"):
        self.fs = 44100
        self.chunk_duration = 5  # seconds
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

    def play_notification_sound(self, sound_file):
        playsound(sound_file)

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
            total_frames = sum(len(chunk) for chunk in self.recording)
            if total_frames >= self.chunk_size:
                self.process_chunk()

    def process_chunk(self):
        """
        Process a completed audio chunk for transcription.
        """
        total_frames = sum(len(chunk) for chunk in self.recording)
        if total_frames < self.chunk_size:
            print("Not enough data for a full chunk. Skipping...")
            return

        # audio_data = np.concatenate(self.recording[: self.chunk_size], axis=0)
        # self.recording = self.recording[self.chunk_size :]
        audio_data = np.concatenate(
            self.recording[: self.chunk_size // len(self.recording[0])], axis=0
        )
        self.recording = self.recording[self.chunk_size // len(self.recording[0]) :]
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
        Transcribe a given audio data array using the Whisper pipeline without file I/O.
        """
        try:
            # Resample the audio data to 16 kHz (required by Whisper)
            audio_data_resampled = librosa.resample(
                y=audio_data.flatten(), orig_sr=self.fs, target_sr=16000
            )

            # Whisper expects the audio input as a numpy array normalized to the range [-1, 1]
            transcription = self.pipeline(audio_data_resampled)["text"]
            return transcription
        except Exception as e:
            print(f"Error during transcription: {e}")
            return "Transcription error occurred."

    def transcribe(self, audio_file_path):
        """
        For uploding audio file
        """
        try:
            audio_input, _ = librosa.load(audio_file_path, sr=16000)
            transcription = self.pipeline(audio_input, batch_size=8)["text"]
            return transcription
        except Exception as e:
            print(f"Error transcribing audio file: {e}")
            return "Error processing the audio file."
