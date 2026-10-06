# Product Requirements Document (PRD)

## Project: Local Offline Speech-to-Text (STT) Platform & Benchmark Engine
**Version:** 1.0.0  
**Author:** Divyansh Prajapati  
**Repository:** [github.com/divyprj/speech-to-text](https://github.com/divyprj/speech-to-text)  
**Live Demo:** [speech-to-text-cm9k.onrender.com](https://speech-to-text-cm9k.onrender.com)  

---

## 1. Executive Summary & Vision

The **Local Offline Speech-to-Text Platform** is an enterprise-ready, high-accuracy, privacy-first audio transcription platform running entirely on consumer-grade CPU hardware without external API dependencies or cloud telemetry.

Powered by **OpenAI Whisper** and a lightweight **FastAPI** asynchronous backend with an interactive dark-mode Single Page Application (SPA), the system solves three critical challenges:
1. **Absolute Data Privacy:** Zero audio packets leave the local host or container environment, ensuring compliance with strict privacy regulations (HIPAA, GDPR, enterprise NDAs).
2. **Accessible Hardware Compatibility:** Real-time and faster-than-real-time performance running purely on consumer multi-core CPUs without requiring expensive CUDA GPUs.
3. **Rigorous Quality Verification:** An automated 50-sample Harvard sentences benchmark engine measuring Word Error Rate (WER), Character Error Rate (CER), Real-Time Factor (RTF), and CPU memory efficiency across diverse acoustic conditions.

---

## 2. Target Personas & Use Cases

| Persona | Primary Goal | Critical Need |
| :--- | :--- | :--- |
| **Enterprise Researcher / Legal Analyst** | Transcribe confidential meetings, interviews, and depositions. | 100% local processing; zero data transmission to third-party AI APIs. |
| **Developer / ML Engineer** | Benchmark and evaluate open-source speech recognition models on local CPU rigs. | Standardized test dataset, automated WER calculation, and latency instrumentation. |
| **Content Creator / Subtitle Editor** | Generate millisecond-precise subtitles and transcripts for videos. | Timestamp-synchronized playback and instant SRT/VTT/JSON/TXT export. |
| **Everyday User / Note Taker** | Dictate notes in real-time through a browser interface. | Low latency, responsive visual feedback, and one-click execution. |

---

## 3. Product Goals & Success Metrics

| Goal | Target Metric | Achieved Benchmark |
| :--- | :--- | :--- |
| **Transcription Accuracy** | Overall WER < 15.0% on clean & technical English | **12.52%** overall WER (5.75% Clean, 2.02% Technical) |
| **Character Fidelity** | Overall CER < 10.0% | **7.93%** CER |
| **Inference Speed** | Real-Time Factor (RTF) < 0.8 (Faster than playback) | **0.547 RTF** (~1.83× faster than real-time) |
| **Memory Footprint** | Local: < 1.5 GB RAM; Cloud: < 512 MB RAM | **305 MB** (Idle/Base) to **785 MB** (Small model) |
| **Privacy Guarantee** | 0 external network requests during transcription | **100% Offline** (local PyTorch weights) |
| **Zero-Setup Usability** | Single-click execution on Windows | Single-click `run.bat` auto-launches UI |

---

## 4. Functional Requirements

### 4.1. Voice Dictation Mode (Live Microphone)
- **FR-1.1:** Support browser-based audio capture using the Web Audio API and `MediaRecorder` with 16 kHz sampling.
- **FR-1.2:** Render a real-time animated waveform canvas reflecting microphone volume and frequency activity.
- **FR-1.3:** Provide live elapsed recording timer, pause/resume, and stop capabilities.
- **FR-1.4:** Automatically stream recorded audio blobs to the local backend upon stopping.

### 4.2. File Upload & Batch Processing
- **FR-2.1:** Drag-and-drop and native file picker supporting `.wav`, `.mp3`, `.m4a`, `.flac`, and `.ogg`.
- **FR-2.2:** Single-worker FIFO background queue with asynchronous job polling (`QUEUED` → `TRANSCRIBING` → `COMPLETED` / `FAILED`).
- **FR-2.3:** Live visual progress indicator showing percent complete and current stage message.

### 4.3. Interactive Synced Transcript Player
- **FR-3.1:** Display full transcribed text alongside interactive word- and sentence-level timecoded segment chips.
- **FR-3.2:** Active segment highlighting synchronized to the HTML5 audio element's `timeupdate` playback events.
- **FR-3.3:** Seeking: Clicking any segment chip instantly seeks the audio player to that exact millisecond timestamp.
- **FR-3.4:** Real-time text search with live highlight matches and match counters.
- **FR-3.5:** Multi-format export: One-click export to **Plain Text (.txt)**, **SubRip (.srt)**, **WebVTT (.vtt)**, and **Structured JSON (.json)**.

### 4.4. Automated Quality & Benchmark Engine
- **FR-4.1:** Built-in standardized 50-sample Harvard sentences benchmark covering:
  - Clean Harvard sentences (10 samples)
  - Conversational phrases (10 samples)
  - Technical & engineering terminology (10 samples)
  - Variable cadence / speech rates (5 samples)
  - Acoustic background noise variations (5 samples)
  - Numeric, monetary, and date formats (10 samples)
- **FR-4.2:** Detailed categorical breakdown calculating WER, CER, latency, and RTF per category.
- **FR-4.3:** Slide-out inspection drawer displaying ground-truth reference, model hypothesis, inline audio player, and error differential.

### 4.5. Hardware & Thread Management
- **FR-4.4:** Real-time system monitoring exposing host OS, physical/logical CPU core count, system RAM, and process RSS memory.
- **FR-4.5:** Dynamic CPU thread allocation (2 to 16 threads) via `torch.set_num_threads()` without restarting the server.
- **FR-4.6:** Model selector supporting Whisper `tiny` (39M), `base` (74M), and `small` (244M) with automatic caching and garbage collection.

---

## 5. Non-Functional Requirements (NFR)

### 5.1. Performance & Latency
- The system must process standard audio clips under 10 seconds within 3 seconds on an 8-core CPU.
- The web interface must initialize and load static assets within 1.5 seconds.

### 5.2. Memory & Resource Safety
- Memory leaks must be prevented by issuing explicit `gc.collect()` passes before and after inference.
- Cloud container deployments must detect containerized memory ceilings (e.g. Render 512 MB Free tier) and automatically constrain to lightweight models (`base`/`tiny`) and 2 CPU threads to prevent OOM termination.

### 5.3. Portability & Deployment
- Must run natively on Windows 10/11 with `run.bat` launcher.
- Must run containerized on Linux via multi-stage Docker build with PyTorch CPU wheel.
- Must deploy seamlessly to cloud PaaS (Render, Fly.io, Hugging Face) using Infrastructure as Code (`render.yaml`).

---

## 6. Assumptions & Constraints

1. **Hardware Baseline:** Target machine is assumed to have at least a dual-core CPU with 4 GB RAM. No GPU is required.
2. **Audio Pre-processing:** Whisper requires 16 kHz mono float32 PCM input. Non-compliant audio inputs are automatically normalized via `ffmpeg` / `soundfile`.
3. **Number Formatting:** Whisper utilizes automatic inverse text normalization (e.g. "fifteen percent" → "15%"). This is accounted for in evaluation documentation.
