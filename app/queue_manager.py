"""
app/queue_manager.py
Single-worker background job queue.
Ensures CPU inference is processed sequentially to prevent CPU oversubscription
and keeps the FastAPI async event loop completely unblocked and responsive.
"""

import time
import uuid
import queue
import threading
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from app.engine import WhisperEngine


@dataclass
class Job:
    id: str
    filename: str
    filepath: str
    model: str
    language: str
    status: str = "QUEUED"  # QUEUED, TRANSCRIBING, COMPLETED, FAILED, CANCELLED
    progress: int = 0
    message: str = "In queue..."
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    cancel_requested: bool = False


class JobQueue:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def submit_job(self, filename: str, filepath: str, model: str = "small", language: str = "en") -> Job:
        job_id = str(uuid.uuid4())[:8]
        job = Job(
            id=job_id,
            filename=filename,
            filepath=filepath,
            model=model,
            language=language,
            status="QUEUED",
            progress=5,
            message="Waiting in queue..."
        )
        with self._lock:
            self.jobs[job_id] = job
        self.task_queue.put(job_id)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self.jobs.get(job_id)
            if job and job.status in ["QUEUED", "TRANSCRIBING"]:
                job.cancel_requested = True
                job.status = "CANCELLED"
                job.message = "Transcription cancelled by user."
                job.completed_at = time.time()
                return True
        return False

    def _worker_loop(self):
        """Worker loop that handles one transcription job at a time."""
        while True:
            job_id = self.task_queue.get()
            try:
                with self._lock:
                    job = self.jobs.get(job_id)
                if not job or job.cancel_requested:
                    self.task_queue.task_done()
                    continue

                # Mark transcribing
                job.status = "TRANSCRIBING"
                job.progress = 25
                job.message = f"Transcribing audio with Whisper '{job.model}'..."

                # Execute transcription
                result = WhisperEngine.transcribe(
                    audio_path=job.filepath,
                    model_name=job.model,
                    language=job.language
                )

                if job.cancel_requested:
                    job.status = "CANCELLED"
                    job.message = "Cancelled."
                else:
                    job.status = "COMPLETED"
                    job.progress = 100
                    job.message = "Transcription completed successfully."
                    job.result = result
                    job.completed_at = time.time()

            except Exception as e:
                with self._lock:
                    job = self.jobs.get(job_id)
                    if job:
                        job.status = "FAILED"
                        job.progress = 100
                        job.error = str(e)
                        job.message = "We couldn't process this audio. The file may be corrupted or unsupported."
                        job.completed_at = time.time()
            finally:
                self.task_queue.task_done()
