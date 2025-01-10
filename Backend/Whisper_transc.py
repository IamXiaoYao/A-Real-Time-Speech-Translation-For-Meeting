import librosa
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor


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

    def save_recording(self, file_name="Recording.wav"):
        if self.recording:
            wav.write(file_name, self.fs, (self.recording * 32767).astype(np.int16))
        else:
            print("No recording found to save.")

    def transcribe(self, file_name="Recording.wav"):
        """
        Records audio and saves it to a specified file.
        :param duration: Duration of recording in seconds.
        :param fs: Sampling rate (default: 44100 Hz).
        """
        if not file_name:
            print("No audio file provided for transcription.")
            return ""
        # Load and preprocess audio
        audio_input, _ = librosa.load(file_name, sr=16000)
        inputs = self.processor(
            audio_input, sampling_rate=16000, return_tensors="pt", language="en"
        )

        # Transcription
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(device)
        input_features = inputs.input_features.to(device)

        generated_ids = self.model.generate(input_features)
        transcription = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )
        return transcription[0]


# whisper_translator = WhisperTransc()
# transcription = whisper_translator.transcribe()
# print("Transcription:", transcription)