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

    def transcribe(self, duration=10, fs=44100, language="en"):

        print("Recording...")
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        print("Recording complete!")
        wav.write("Recording.wav", fs, myrecording)
        audio_input, _ = librosa.load("Recording.wav", sr=16000)
        inputs = self.processor(
            audio_input, sampling_rate=16000, return_tensors="pt", language=language
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Transcription
        input_features = inputs.input_features.to(device)
        self.model = self.model.to(device)

        generated_ids = self.model.generate(input_features)
        transcription = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )
        return transcription[0]


whisper_translator = WhisperTransc()
transcription = whisper_translator.transcribe()
print("Transcription:", transcription)
