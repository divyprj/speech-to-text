"""
app/routes.py
FastAPI API route handlers for local speech-to-text operations.
"""

import os
import sys
import csv
import json
import psutil
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional

from app.engine import ModelManager, WhisperEngine
from app.queue_manager import JobQueue

router = APIRouter(prefix="/api")

ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT_DIR / "data" / "uploads"
AUDIO_SAMPLES_DIR = ROOT_DIR / "audio_samples"
RESULTS_CSV = ROOT_DIR / "results.csv"
METRICS_TXT = ROOT_DIR / "output" / "metrics.txt"
TRANSCRIPTS_CSV = ROOT_DIR / "transcripts" / "transcripts.csv"

os.makedirs(UPLOAD_DIR, exist_ok=True)


class SettingsPayload(BaseModel):
    model: Optional[str] = "small"
    threads: Optional[int] = os.cpu_count() or 4
    language: Optional[str] = "en"


@router.get("/health")
def get_health():
    return {"status": "ok", "offline": True, "app": "Local Transcriber"}


@router.get("/system")
def get_system_info():
    mm = ModelManager.get_instance()
    mem = psutil.virtual_memory()
    proc = psutil.Process()
    return {
        "os": sys.platform,
        "cpu_count": os.cpu_count() or 1,
        "configured_threads": mm.cpu_threads,
        "active_model": mm.active_model_name or "small",
        "available_models": [
            {"id": "tiny", "name": "Tiny (Quick)", "params": "39M", "speed": "Very Fast", "quality": "Good"},
            {"id": "base", "name": "Base (Balanced)", "params": "74M", "speed": "Fast", "quality": "High"},
            {"id": "small", "name": "Small (Accurate)", "params": "244M", "speed": "Balanced", "quality": "Very High"}
        ],
        "ram_total_gb": round(mem.total / (1024**3), 1),
        "ram_available_gb": round(mem.available / (1024**3), 1),
        "process_ram_mb": round(proc.memory_info().rss / (1024**2), 1)
    }


@router.get("/settings")
def get_settings():
    mm = ModelManager.get_instance()
    return {
        "model": mm.active_model_name or "small",
        "threads": mm.cpu_threads,
        "language": "en"
    }


@router.put("/settings")
def update_settings(payload: SettingsPayload):
    mm = ModelManager.get_instance()
    if payload.threads:
        mm.set_threads(payload.threads)
    if payload.model and payload.model in ["tiny", "base", "small"]:
        # Pre-warm or switch
        mm.get_model(payload.model)
    return {"status": "updated", "model": mm.active_model_name, "threads": mm.cpu_threads}


@router.post("/transcribe")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    model: str = Form("small"),
    language: str = Form("en")
):
    safe_name = os.path.basename(file.filename or "upload.wav")
    dest_path = UPLOAD_DIR / safe_name
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    jq = JobQueue.get_instance()
    job = jq.submit_job(
        filename=safe_name,
        filepath=str(dest_path),
        model=model,
        language=language
    )
    return {"job_id": job.id, "status": job.status, "filename": safe_name}


@router.post("/record")
async def transcribe_recorded_audio(
    file: UploadFile = File(...),
    model: str = Form("small"),
    language: str = Form("en")
):
    import time
    timestamp = int(time.time())
    safe_name = f"voice_dictation_{timestamp}.webm"
    dest_path = UPLOAD_DIR / safe_name
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    jq = JobQueue.get_instance()
    job = jq.submit_job(
        filename=safe_name,
        filepath=str(dest_path),
        model=model,
        language=language
    )
    return {"job_id": job.id, "status": job.status, "filename": safe_name}


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    jq = JobQueue.get_instance()
    job = jq.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "filename": job.filename,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "result": job.result,
        "error": job.error,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    jq = JobQueue.get_instance()
    success = jq.cancel_job(job_id)
    return {"cancelled": success}


@router.get("/jobs/{job_id}/export/{fmt}")
def export_job_result(job_id: str, fmt: str):
    jq = JobQueue.get_instance()
    job = jq.get_job(job_id)
    if not job or not job.result:
        raise HTTPException(status_code=404, detail="Transcript result not found")

    res = job.result
    base_stem = Path(job.filename).stem

    if fmt == "txt":
        return PlainTextResponse(
            content=res.get("text", ""),
            headers={"Content-Disposition": f'attachment; filename="{base_stem}.txt"'}
        )
    elif fmt == "srt":
        srt_content = WhisperEngine.generate_srt(res.get("segments", []))
        return PlainTextResponse(
            content=srt_content,
            headers={"Content-Disposition": f'attachment; filename="{base_stem}.srt"'}
        )
    elif fmt == "vtt":
        vtt_content = WhisperEngine.generate_vtt(res.get("segments", []))
        return PlainTextResponse(
            content=vtt_content,
            headers={"Content-Disposition": f'attachment; filename="{base_stem}.vtt"'}
        )
    elif fmt == "json":
        return Response(
            content=json.dumps(res, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{base_stem}.json"'}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: txt, srt, vtt, json")


@router.get("/benchmark")
def get_benchmark_data():
    """Retrieve structured benchmark dataset and results for the Quality Dashboard."""
    samples = []
    if RESULTS_CSV.exists():
        with open(RESULTS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                samples.append(row)

    categories = {}
    if TRANSCRIPTS_CSV.exists():
        with open(TRANSCRIPTS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fname = row.get("filename")
                cat = row.get("category", "General")
                if fname:
                    categories[fname] = cat

    # Attach category to results
    for s in samples:
        fname = s.get("audio_file")
        s["category"] = categories.get(fname, "General")

    # Global summary stats
    metrics_text = ""
    if METRICS_TXT.exists():
        with open(METRICS_TXT, "r", encoding="utf-8") as f:
            metrics_text = f.read()

    return {
        "total_samples": len(samples),
        "metrics_summary": metrics_text,
        "samples": samples
    }


@router.get("/audio/{filename}")
def stream_audio_file(filename: str):
    """Stream audio sample for in-browser playback."""
    # Check uploads
    p1 = UPLOAD_DIR / filename
    if p1.exists():
        return FileResponse(p1)

    # Check benchmark audio_samples
    p2 = AUDIO_SAMPLES_DIR / filename
    if p2.exists():
        return FileResponse(p2)

    raise HTTPException(status_code=404, detail="Audio file not found")
