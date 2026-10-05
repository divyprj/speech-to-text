## Local Speech-to-Text Platform v1.0.0

A high-performance, private, 100% offline Speech-to-Text application powered by OpenAI Whisper and FastAPI. Engineered with a Linear/Descript-level enterprise SaaS interface, interactive timestamp-synchronized audio playback, in-page keyword search, sequential batch queue processing, and a standardized 50-sample Harvard sentences benchmark evaluation suite.

### Key Features
- **Local Speech Recognition:** Fully offline CPU inference with multi-core thread tuning (`Tiny`, `Base`, and `Small` Whisper models).
- **Interactive Audio-Synced Transcript:** Click any transcript segment timestamp (`▶ 00:12`) to seek audio playback; active segment highlights automatically as audio plays.
- **In-Page Transcript Search:** Live keyword matching with match counters and yellow highlight markers.
- **Batch Processing Queue:** Sequential FIFO queue handling multiple uploaded audio files with zero CPU oversubscription.
- **Microphone Dictation with Waveform:** Live HTML5 Canvas audio spectrum feedback and dynamic recording state machine.
- **Bespoke SVG Icon System:** Canonical 24×24, 1.75px stroke design language with zero emojis.
- **Keyboard Shortcuts:** `Space` for play/pause, `Esc` to close modal/drawer, `Ctrl+C` for transcript copy, `Ctrl+F` for transcript search, `←/→` for audio seeking.
- **Full Benchmark Evaluation:** 50 Harvard sentences evaluated with automated Word Error Rate (WER: 12.52%), Character Error Rate (CER: 10.98%), and Real-Time Factor (RTF: 1.83×).
- **Multi-Format Export:** `.txt`, `.srt`, `.vtt`, and `.json`.

### Included Assets
- `submission.zip`: Complete production package including source code, benchmark dataset, scripts, and high-resolution screenshots.
