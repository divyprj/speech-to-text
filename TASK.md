# Task Tracking & Engineering Roadmap (TASK.md)

## Project: Local Offline Speech-to-Text Platform & Benchmark Engine
**Tracking Version:** 1.0.0  
**Status:** All Primary Milestones Completed & Deployed  

---

## 1. Completed Milestones (v1.0.0 Deliverables)

### Milestone 1: Core Offline Speech Recognition Engine
- [x] Integrate OpenAI Whisper running purely on local CPU hardware.
- [x] Build multi-format audio pre-processor (`soundfile` / `ffmpeg`) normalizing input to 16 kHz mono float32 PCM.
- [x] Implement thread-safe `ModelManager` singleton supporting dynamic model switching (`tiny`, `base`, `small`).
- [x] Configure PyTorch linear algebra multi-threading (`torch.set_num_threads`).
- [x] Build multi-format transcript export engine (TXT, SubRip SRT, WebVTT, and structured JSON).

### Milestone 2: 50-Sample Harvard Benchmark Suite
- [x] Generate standardized 50-clip audio dataset across 6 acoustic conditions (Clean, Conversational, Technical, Cadence, Noise, Numeric).
- [x] Author matching ground-truth reference transcripts in `transcripts/transcripts.csv`.
- [x] Implement evaluation pipeline calculating Word Error Rate (WER) and Character Error Rate (CER) via Levenshtein edit distance.
- [x] Implement latency, CPU time, and Real-Time Factor (RTF) instrumentation.
- [x] Generate comprehensive evaluation report (`output/metrics.txt` and `report.md`).
- [x] Achieve target metrics: **12.52% overall WER**, **7.93% CER**, and **0.547 RTF** (~1.83× faster than real-time).

### Milestone 3: Modern Dark SaaS User Interface
- [x] Design and implement 4-tab Single Page Application (`Dictate`, `Files`, `Quality`, `Settings`).
- [x] Implement real-time Web Audio API recording with animated HTML5 Canvas waveform visualizer.
- [x] Build interactive Audio-Synchronized Transcript Player with word/sentence-level seeking and cue highlighting.
- [x] Implement client-side in-page transcript search with live highlight matching and counter.
- [x] Create Quality tab with interactive 50-sample dataset explorer table and slide-out sample inspection drawer.
- [x] Create Settings tab with live CPU core detection, memory telemetry, and thread sliders.

### Milestone 4: Packaging, Releases & Automation
- [x] Write one-click Windows launcher (`run.bat`) with auto-environment detection and CLI submenu.
- [x] Package standalone evaluation archive (`submission.zip`).
- [x] Publish official GitHub Release [`v1.0.0`](https://github.com/divyprj/speech-to-text/releases/tag/v1.0.0) with attached binaries.
- [x] Capture and embed comprehensive screenshot gallery in `README.md`.

### Milestone 5: Production Containerization & Cloud Deployment
- [x] Author multi-stage, slim `Dockerfile` with CPU-optimized PyTorch build.
- [x] Pre-cache Whisper model weights during Docker build for instant container boot.
- [x] Create Infrastructure-as-Code Blueprint (`render.yaml`) for 1-click cloud deployment.
- [x] Implement memory guardrail for Render 512 MB Free tier (automatic routing to Whisper `base` and proactive `gc.collect()` sweeps).
- [x] Successfully deploy live production web service: [speech-to-text-cm9k.onrender.com](https://speech-to-text-cm9k.onrender.com).

---

## 2. Active Operational Status

| Component | Status | Environment | Endpoint / Location |
| :--- | :--- | :--- | :--- |
| **Cloud Web App** | 🟢 Live & Healthy | Render Cloud (Docker) | `https://speech-to-text-cm9k.onrender.com` |
| **GitHub Repository** | 🟢 Public & Up-to-date | GitHub (`main`) | `https://github.com/divyprj/speech-to-text` |
| **GitHub Release v1.0.0** | 🟢 Published | GitHub Releases | `https://github.com/divyprj/speech-to-text/releases/tag/v1.0.0` |
| **Local Desktop Launcher** | 🟢 Verified | Windows (`stt-env`) | `run.bat` (Port 8765) |
| **Benchmark Suite** | 🟢 Verified | Local & CLI | `results.csv`, `output/metrics.txt` |

---

## 3. Future Roadmap & Backlog

### v1.1.0 — Inference Acceleration & Voice Activity Detection (Upcoming)
- [ ] **CTranslate2 / faster-whisper Integration:**
  - Transition model backend to CTranslate2 for INT8 and INT16 quantized inference.
  - Target: Reduce CPU RAM consumption to < 200 MB and achieve 3.5×–4.0× real-time speed.
- [ ] **Silero VAD (Voice Activity Detection):**
  - Integrate Silero VAD to strip silent intervals prior to Whisper token generation.
  - Target: 25%–35% reduction in compute time for real-world conversational audio.

### v1.2.0 — Multi-Language & Translation Expansion
- [ ] Auto-language detection toggle in UI with language confidence score.
- [ ] One-click translation from 99 source languages directly to English transcript.
- [ ] Side-by-side bilingual transcript export.

### v2.0.0 — Streaming Audio & Speaker Diarization
- [ ] **WebSocket Streaming Inference:**
  - Implement real-time partial hypothesis streaming using sliding window audio chunks.
- [ ] **Speaker Diarization:**
  - Integrate PyAnnote.audio to detect and assign speaker labels (`Speaker A`, `Speaker B`) to transcript segments.
