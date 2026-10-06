# Engineering Rules & Guidelines (RULESS.md)

## Project: Local Offline Speech-to-Text Platform & Benchmark Engine
**Document Version:** 1.0.0  
**Status:** Mandatory for all contributors  

---

## 1. Core Engineering Principles

### 1.1. Absolute Offline & Privacy Guarantee (Zero Cloud Leakage)
- **Rule 1.1.1:** Never introduce network calls, remote API endpoints (e.g. OpenAI API, Google Cloud Speech, external analytics), or cloud telemetry during audio ingestion, transcription, or evaluation.
- **Rule 1.1.2:** All ML model weights must reside locally on disk or be pre-baked into the container image during build time.
- **Rule 1.1.3:** Never link to external CDNs in HTML templates (e.g., Google Fonts, cdnjs, unpkg, tailwind CDN). All fonts, icons, CSS, and JS must be self-contained in `static/`.

### 1.2. Memory Hygiene & Resource Constraints
- **Rule 1.2.1:** Never allow multiple Whisper model instances to reside simultaneously in RAM. Any switch between `tiny`, `base`, and `small` must invoke `del self.active_model` followed by `gc.collect()`.
- **Rule 1.2.2:** In cloud container environments (e.g., Render Free Tier with a 512 MB hard memory ceiling), large models must be gracefully intercepted and clamped to lightweight variants (`base` or `tiny`).
- **Rule 1.2.3:** Limit PyTorch CPU linear algebra threads in constrained environments to avoid thread-local memory spikes. Always use `torch.set_num_threads()` defensively.

---

## 2. Backend Code Standards (Python & FastAPI)

### 2.1. Code Quality & Typing
- Use Python 3.10+ typing syntax (`str`, `dict`, `list`, `Optional[int]`).
- All API request and response bodies must be structured with Pydantic models.
- Maintain documentation integrity: all public functions and classes must have clear, explanatory docstrings with parameters and return types.

### 2.2. Error Handling & Sanitization
- File uploads must never trust user-supplied filenames. Always sanitize paths using `os.path.basename()` before writing to `data/uploads/`.
- Handle corrupted or non-audio file inputs gracefully with meaningful HTTP 400 status codes and user-friendly error messages.
- Always clean up temporary recording files (`.webm`, `.wav`) when jobs complete or fail.

### 2.3. Asynchronous Execution & Concurrency
- Never perform blocking CPU-bound ML inference directly within asynchronous FastAPI route handlers (`async def`).
- Route all transcription tasks through `JobQueue.submit_job()`, allowing the dedicated daemon background worker thread to execute inference sequentially.
- Return immediate response tokens (`job_id`) with HTTP 200/202, enabling clients to poll status predictably.

---

## 3. Frontend Standards (HTML / CSS / JavaScript)

### 3.1. Framework-Free Architecture
- Keep the frontend dependency-free: Use vanilla ES6+ JavaScript and modern semantic HTML5. Do not introduce bloated frameworks (React, Angular, Vue) for simple Single Page Applications.
- Do not use jQuery or external UI widget bundles.

### 3.2. Design System & CSS Rules
- All colors, elevations, typography scales, and border-radii must be declared as CSS custom properties (`var(--bg-main)`, `var(--brand-primary)`, etc.) in `static/css/style.css`.
- Support responsive viewport breakpoints down to 768px (tablets and mobile browsers).
- Form inputs, buttons, and drawer cards must have clean focus outlines, smooth CSS transitions (150ms–200ms cubic-bezier), and consistent hover feedback.

### 3.3. Web Audio API Best Practices
- Always check for browser `navigator.mediaDevices.getUserMedia` capability before prompting for microphone access.
- Always properly close or disconnect `AudioContext` and `MediaStream` tracks when stopping recordings to release the physical microphone hardware lock.

---

## 4. Benchmark & Evaluation Rules

### 4.1. Dataset Integrity
- Ground-truth reference transcripts in `transcripts/` and audio files in `audio_samples/` are immutable benchmarks. Never modify audio samples without updating `transcripts.csv` and re-running `code/evaluate.py`.
- Audio samples must remain standardized at **16 kHz, 16-bit mono PCM WAV** to eliminate resampling bias.

### 4.2. Metric Reporting Standards
- Always report both **Word Error Rate (WER)** and **Character Error Rate (CER)**.
- For financial and numeric phrases, explicitly note Whisper's Inverse Text Normalization (ITN) behavior (e.g. converting "fifteen percent" to "15%").
- When quoting Real-Time Factor (RTF), always document the host CPU specification (core count and model) to maintain scientific reproducibility.

---

## 5. Git & Deployment Rules

### 5.1. Conventional Commit Messages
Commit messages must adhere to the Conventional Commits specification:
- `feat:` New features or UI components.
- `fix:` Bug fixes, port adjustments, memory patches.
- `perf:` Inference latency or memory footprint optimizations.
- `docs:` Documentation, screenshots, benchmark updates.
- `ci:` Dockerfile, Render blueprints, setup scripts.

### 5.2. Docker & Container Rules
- Base Docker images on slim Debian distributions (`python:3.11-slim`).
- Install system dependencies (`ffmpeg`, `libsndfile1`) in a single `RUN` layer and clean `/var/lib/apt/lists/*` to minimize image size.
- Pre-cache model weights during image build so containers boot instantly upon launch.
- Never hardcode dynamic ports: always read `os.environ.get("PORT", "10000")` and bind to `0.0.0.0`.
