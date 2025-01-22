import json
import sys

import librosa
import numpy as np
import sounddevice as sd
import torch
from transformers import pipeline


class WhisperTransc:
    def __init__(self, model_name="openai/whisper-base.en"):
        self.fs = 44100
        self.chunk_duration = 3  # chunk seconds
        self.chunk_size = int(self.fs * self.chunk_duration)

        self.overlap_seconds = 1  # overlap
        self.overlap_frames = int(self.fs * self.overlap_seconds)

        self.buffer = np.array([], dtype=np.float32)
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
        self.buffer = np.array([], dtype=np.float32)
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
            self.buffer = np.concatenate((self.buffer, indata.flatten()))

            while len(self.buffer) >= self.chunk_size:
                chunk_data = self.buffer[: self.chunk_size]
                self.process_chunk(chunk_data)
                start_idx = self.chunk_size - self.overlap_frames
                self.buffer = self.buffer[start_idx:]

    def process_chunk(self, audio_data):
        """
        Transcribe this chunk of audio_data and pass it to the callback if exists.
        """
        print("Processing chunk for transcription...")
        transcription = self.transcribe_audio(audio_data)

        if hasattr(self, "update_callback"):
            self.update_callback(transcription)

    def stop_recording(self):
        """
        Stop recording audio.
        """
        self.is_recording = False
        print("Stopping recording and processing remaining audio...")

        while len(self.buffer) >= self.chunk_size:
            # Extract the first chunk_size frames
            chunk_data = self.buffer[: self.chunk_size]
            self.process_chunk(chunk_data)
            start_idx = self.chunk_size - self.overlap_frames
            self.buffer = self.buffer[start_idx:]

        if len(self.buffer) > 0:
            print("Processing leftover audio (smaller than one chunk)...")
            transcription = self.transcribe_audio(self.buffer)
            if hasattr(self, "update_callback"):
                self.update_callback(transcription)

        self.buffer = np.array([], dtype=np.float32)

    def transcribe_audio(self, audio_data):
        """
        Transcribe a given audio data array using the Whisper pipeline without file I/O.
        """
        try:
            audio_data_resampled = librosa.resample(
                y=audio_data.flatten(), orig_sr=self.fs, target_sr=16000
            )

            # Whisper expects the audio input as a numpy array normalized to the range [-1, 1]
            transcription = self.pipeline(inputs=audio_data_resampled, batch_size=8)[
                "text"
            ]
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


def main():
    whisper = WhisperTransc()

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        try:
            request = json.loads(line)
            command = request.get("command")
            args = request.get("args", [])
            kwargs = request.get("kwargs", {})

            if hasattr(whisper, command):
                method = getattr(whisper, command)
                if callable(method):
                    result = method(*args, **kwargs)
                    print(json.dumps({"result": result}))
                else:
                    print(json.dumps({"error": f"Command {command} is not callable."}))
            else:
                print(json.dumps({"error": f"Command {command} not found."}))
        except Exception as e:
            print(json.dumps({"error": str(e)}))

        sys.stdout.flush()


if __name__ == "__main__":
    main()
