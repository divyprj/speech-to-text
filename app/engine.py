"""
app/engine.py
Thread-safe Whisper Engine and Model Manager.
Handles lazy model loading, CPU thread allocation, audio preprocessing,
transcription execution, and export formatting (TXT, SRT, VTT, JSON).
"""

import os
import sys
import gc
import time
import threading
import soundfile as sf
import torch
import whisper


def format_timestamp(seconds: float, srt_format: bool = False) -> str:
    """Format seconds into HH:MM:SS,mmm (SRT) or HH:MM:SS.mmm (VTT)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    sep = "," if srt_format else "."
    return f"{hrs:02d}:{mins:02d}:{secs:02d}{sep}{msecs:03d}"


class ModelManager:
    """Manages active Whisper model instance with thread safety."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.active_model_name = None
        self.active_model = None
        self.cpu_threads = os.cpu_count() or 4
        torch.set_num_threads(self.cpu_threads)

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def set_threads(self, threads: int):
        with self._lock:
            self.cpu_threads = max(1, int(threads))
            torch.set_num_threads(self.cpu_threads)

    def get_model(self, model_name: str = None):
        """Load or return the cached Whisper model, freeing prior models if different."""
        if not model_name:
            model_name = "base" if os.environ.get("RENDER") else "small"
        with self._lock:
            if self.active_model is not None and self.active_model_name == model_name:
                return self.active_model

            # Clean up old model from memory
            if self.active_model is not None:
                del self.active_model
                self.active_model = None
                gc.collect()

            print(f"[ModelManager] Loading Whisper '{model_name}' on CPU ({self.cpu_threads} threads)...", flush=True)
            t0 = time.perf_counter()
            self.active_model = whisper.load_model(model_name, device="cpu")
            self.active_model_name = model_name
            t1 = time.perf_counter()
            print(f"[ModelManager] Model '{model_name}' loaded in {t1 - t0:.2f}s", flush=True)

            return self.active_model


class WhisperEngine:
    """Performs transcription and generates formatted exports."""

    @staticmethod
    def get_audio_info(file_path: str):
        try:
            info = sf.info(file_path)
            return {
                "duration": float(info.duration),
                "samplerate": info.samplerate,
                "channels": info.channels
            }
        except Exception:
            return {"duration": 0.0, "samplerate": 16000, "channels": 1}

    @classmethod
    def transcribe(cls, audio_path: str, model_name: str = "small", language: str = "en") -> dict:
        mm = ModelManager.get_instance()
        model = mm.get_model(model_name)

        audio_info = cls.get_audio_info(audio_path)
        duration = audio_info.get("duration", 0.0)

        t_start = time.perf_counter()
        cpu_start = time.process_time()

        transcribe_args = {
            "audio": audio_path,
            "verbose": False,
            "fp16": False
        }
        if language and language != "auto":
            transcribe_args["language"] = language

        result = model.transcribe(**transcribe_args)

        latency = time.perf_counter() - t_start
        cpu_time = time.process_time() - cpu_start
        rtf = (duration / latency) if latency > 0 else 0.0

        full_text = result.get("text", "").strip()
        raw_segments = result.get("segments", [])

        parsed_segments = []
        for s in raw_segments:
            parsed_segments.append({
                "id": s.get("id", 0),
                "start": round(s.get("start", 0.0), 2),
                "end": round(s.get("end", 0.0), 2),
                "text": s.get("text", "").strip()
            })

        return {
            "text": full_text,
            "duration": round(duration, 2),
            "latency": round(latency, 2),
            "cpu_time": round(cpu_time, 2),
            "rtf": round(rtf, 2),
            "model": model_name,
            "language": result.get("language", language),
            "segments": parsed_segments
        }

    @staticmethod
    def generate_srt(segments: list) -> str:
        lines = []
        for idx, seg in enumerate(segments, start=1):
            start_str = format_timestamp(seg["start"], srt_format=True)
            end_str = format_timestamp(seg["end"], srt_format=True)
            lines.append(f"{idx}\n{start_str} --> {end_str}\n{seg['text']}\n")
        return "\n".join(lines)

    @staticmethod
    def generate_vtt(segments: list) -> str:
        lines = ["WEBVTT\n"]
        for seg in segments:
            start_str = format_timestamp(seg["start"], srt_format=False)
            end_str = format_timestamp(seg["end"], srt_format=False)
            lines.append(f"{start_str} --> {end_str}\n{seg['text']}\n")
        return "\n".join(lines)
