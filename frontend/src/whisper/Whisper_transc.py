import librosa
import numpy as np
import sounddevice as sd
import torch
import sys
import json
import threading
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

    def safe_print(self, data):
        """
        Ensures proper JSON formatting for Node.js
        """
        try:
            print(json.dumps(data))  # Always output valid JSON
        except Exception as e:
            print(json.dumps({"error": f"JSON Encoding Error: {str(e)}"}))
        sys.stdout.flush()

    def record_audio(self):
        """
        Start recording in a separate thread so it doesn't block command processing.
        """
        if self.is_recording:
            self.safe_print({"error": "Already recording"})
            return

        self.safe_print({"status": "recording started"})

        self.is_recording = True
        self.buffer = np.array([], dtype=np.float32)

        def recording_thread():
            with sd.InputStream(
                samplerate=self.fs,
                channels=1,
                callback=self.audio_callback,
                dtype="float32",
            ):
                while self.is_recording:
                    sd.sleep(100)  # Allow other commands to be processed

        thread = threading.Thread(target=recording_thread, daemon=True)
        thread.start()

    def audio_callback(self, indata, frames, time, status):
        """
        Callback to append recorded audio data to `self.buffer`.
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
        Transcribe this chunk of audio_data and send it as output.
        """
        transcription = self.transcribe_audio(audio_data)
        if transcription and transcription.strip():  # Ensure no empty duplicate messages
            self.safe_print({"result": transcription})

    def stop_recording(self):
        """
        Stop recording audio and process remaining buffer.
        """
        if not self.is_recording:
            self.safe_print({"error": "Not currently recording"})
            return

        self.is_recording = False
        self.safe_print({"status": "recording stopped"})

        while len(self.buffer) >= self.chunk_size:
            chunk_data = self.buffer[: self.chunk_size]
            self.process_chunk(chunk_data)
            start_idx = self.chunk_size - self.overlap_frames
            self.buffer = self.buffer[start_idx:]

        if len(self.buffer) > 0:
            self.safe_print({"status": "processing leftover audio"})
            transcription = self.transcribe_audio(self.buffer)
            if transcription and transcription.strip():
                self.safe_print({"result": transcription})

        self.buffer = np.array([], dtype=np.float32)

    def transcribe_audio(self, audio_data):
        """
        Transcribe a given audio data array using the Whisper pipeline.
        """
        try:
            audio_data_resampled = librosa.resample(
                y=audio_data.flatten(), orig_sr=self.fs, target_sr=16000
            )
            transcription = self.pipeline(inputs=audio_data_resampled, batch_size=8)["text"]
            return transcription
        except Exception as e:
            self.safe_print({"error": f"Error during transcription: {str(e)}"})
            return "Transcription error occurred."

    def transcribe(self, audio_file_path):
        """
        Transcribe an uploaded audio file.
        """
        try:
            audio_input, _ = librosa.load(audio_file_path, sr=16000)
            transcription = self.pipeline(audio_input, batch_size=8)["text"]
            return transcription
        except Exception as e:
            self.safe_print({"error": f"Error transcribing audio file: {str(e)}"})
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
                    if result is not None:
                        whisper.safe_print({"result": result})
                else:
                    whisper.safe_print({"error": f"Command {command} is not callable."})
            else:
                whisper.safe_print({"error": f"Command {command} not found."})
        except Exception as e:
            whisper.safe_print({"error": str(e)})

if __name__ == "__main__":
    main()