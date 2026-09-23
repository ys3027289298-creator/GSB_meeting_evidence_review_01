import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class AudioNoiseReducer:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.noise_reduction_params = {
            'n_fft': 2048,
            'hop_length': 512,
            'win_length': 2048,
            'noise_sample_duration': 1.0,
        }

    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        logger.info(f"Loading audio file: {audio_path}")
        y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        logger.info(f"Loaded audio: duration={len(y)/sr:.2f}s, sample_rate={sr}")
        return y, sr

    def estimate_noise_profile(self, y: np.ndarray, sr: int) -> np.ndarray:
        noise_duration = self.noise_reduction_params['noise_sample_duration']
        noise_samples = int(noise_duration * sr)
        noise_sample = y[:noise_samples] if len(y) > noise_samples else y
        D_noise = librosa.stft(
            noise_sample,
            n_fft=self.noise_reduction_params['n_fft'],
            hop_length=self.noise_reduction_params['hop_length'],
            win_length=self.noise_reduction_params['win_length']
        )
        noise_mag = np.mean(np.abs(D_noise), axis=1, keepdims=True)
        logger.info("Noise profile estimated from first second of audio")
        return noise_mag

    def reduce_noise(self, y: np.ndarray, sr: int) -> np.ndarray:
        logger.info("Starting noise reduction using spectral subtraction")
        D = librosa.stft(
            y,
            n_fft=self.noise_reduction_params['n_fft'],
            hop_length=self.noise_reduction_params['hop_length'],
            win_length=self.noise_reduction_params['win_length']
        )
        mag, phase = librosa.magphase(D)
        noise_mag = self.estimate_noise_profile(y, sr)
        alpha = 2.0
        beta = 0.01
        mag_clean = np.maximum(mag - alpha * noise_mag, beta * mag)
        D_clean = mag_clean * phase
        y_clean = librosa.istft(
            D_clean,
            hop_length=self.noise_reduction_params['hop_length'],
            win_length=self.noise_reduction_params['win_length']
        )
        logger.info("Noise reduction completed")
        return y_clean

    def apply_preemphasis(self, y: np.ndarray, coefficient: float = 0.95) -> np.ndarray:
        return librosa.effects.preemphasis(y, coef=coefficient)

    def normalize_audio(self, y: np.ndarray) -> np.ndarray:
        peak = np.max(np.abs(y))
        if peak > 0:
            y = y / peak * 0.9
        return y

    def process_audio(self, input_path: str, output_path: str) -> str:
        try:
            y, sr = self.load_audio(input_path)
            y_clean = self.reduce_noise(y, sr)
            y_clean = self.apply_preemphasis(y_clean)
            y_clean = self.normalize_audio(y_clean)
            output_path = str(Path(output_path).with_suffix('.wav'))
            sf.write(output_path, y_clean, sr, format='WAV', subtype='PCM_16')
            logger.info(f"Processed audio saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}", exc_info=True)
            raise
