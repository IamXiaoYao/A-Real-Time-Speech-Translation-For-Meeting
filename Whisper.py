import librosa
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import torch
from playsound import playsound
from transformers import WhisperForConditionalGeneration, WhisperProcessor


class WhisperTransc:
    def __init__(self, model_name="openai/whisper-small"):
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)

    def play_notification_sound(self, sound_file):
        playsound(sound_file)

    def transcribe(self, duration=10, fs=44100):
        """
        :param audio_path: The path to the audio file for transcription.
        :param target_language: The target language code for translation. Defaults to 'en' (English).
        :return: The transcribed and translated text.
        """
        self.play_notification_sound("notification-sound.wav")
        print("Recording...")
        recording = sd.rec(
            int(duration * fs), samplerate=fs, channels=1, dtype="float32"
        )
        sd.wait()
        print("Recording Complete!")
        self.play_notification_sound("notification-sound.wav")

        wav.write("Recording.wav", fs, (recording * 32767).astype(np.int16))

        # Load and preprocess audio
        audio_input, sample_rate = librosa.load("Recording.wav", sr=16000)
        inputs = self.processor(audio_input, sampling_rate=16000, return_tensors="pt")

        # Transcription
        input_features = inputs.input_features.to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = self.model.to("cuda" if torch.cuda.is_available() else "cpu")

        generated_ids = self.model.generate(input_features)
        transcription = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )
        return transcription[0]


whisper_translator = WhisperTransc()
transcription = whisper_translator.transcribe()
print("Transcription:", transcription)
