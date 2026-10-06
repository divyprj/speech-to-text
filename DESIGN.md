# UI/UX Design System & Specification (DESIGN.md)

## Project: Local Offline Speech-to-Text Platform & Benchmark Engine
**Design System Version:** 2.2  
**Theme:** Dark SaaS Professional  
**Target Viewports:** Desktop (1440×900, 1920×1080), Tablet (1024×768), Mobile (375×812)  

---

## 1. Design Vision & Philosophy

The application's visual interface is engineered to evoke the precision, responsiveness, and aesthetic clarity of high-tier developer and ML productivity tools (similar to Linear, Raycast, and Vercel).

Key design pillars:
1. **Dark Mode First:** Deep slate backgrounds (`#0a0d14`, `#10141f`) with high-contrast neutral text reducing eye strain during extended transcription sessions.
2. **Instant Visual Feedback:** Live 60 FPS audio visualizer, animated recording pulses, real-time audio-synced transcript highlighting, and responsive progress bars.
3. **Information Density with Breathing Room:** Clean 8px grid spacing, subtle borders (`rgba(255, 255, 255, 0.08)`), and uncluttered data visualization.

---

## 2. Design Tokens & Color Palette

### 2.1. Color Palette

```css
:root {
  /* Surfaces & Backgrounds */
  --bg-body: #0a0d14;         /* Deep canvas black */
  --bg-surface: #10141f;      /* Primary card and container surface */
  --bg-surface-elevated: #161c2c; /* Hovered cards, drawers, modals */
  --bg-input: #131826;        /* Text inputs, select dropdowns */

  /* Borders & Dividers */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-focus: rgba(99, 102, 241, 0.5);

  /* Typography Colors */
  --text-primary: #f8fafc;    /* High-emphasis headers and body */
  --text-secondary: #94a3b8;  /* Labels, subtitles, metadata */
  --text-muted: #64748b;      /* Disabled items, placeholders */

  /* Accent & Brand Colors */
  --brand-primary: #6366f1;   /* Indigo 500: Primary actions */
  --brand-primary-hover: #4f46e5; /* Indigo 600 */
  --brand-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);

  /* Status Colors */
  --success: #10b981;         /* Emerald: 100% Offline badge, completed jobs */
  --warning: #f59e0b;         /* Amber: Warning notes, processing states */
  --error: #ef4444;           /* Rose: Failed jobs, recording active pulse */
  --info: #3b82f6;            /* Blue: Informational tooltips */
}
```

---

## 3. Typography Scale

The interface uses system font smoothing with an ultra-clean sans-serif stack (`Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`) paired with monospace for timestamps and code.

| Role | Font Size | Weight | Line Height | Letter Spacing | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Page Title** | 28px (`1.75rem`) | 700 (Bold) | 1.2 | -0.02em | Section headers |
| **Section Title** | 18px (`1.125rem`) | 600 (Semibold) | 1.3 | -0.01em | Card groups |
| **Body Primary** | 14px (`0.875rem`) | 400 (Regular) | 1.5 | normal | Transcripts, table text |
| **Metadata / Label** | 12px (`0.75rem`) | 500 (Medium) | 1.4 | +0.02em | Form labels, badges |
| **Timestamp / Monospace** | 12px (`0.75rem`) | 600 (Semibold) | 1.4 | normal | Audio timecodes (`00:04.2`) |

---

## 4. Key Component Specifications

### 4.1. Navigation Header & Status Pill
- **Height:** 64px fixed with subtle bottom border.
- **Brand Identity:** Distinctive glowing icon with "Local Transcriber" title and version badge.
- **Privacy Indicator:** Green pill (`● 100% Offline`) affirming local CPU execution.
- **Tab Navigation:** Segmented controls with active indicator line and 150ms ease transition.

### 4.2. Dictate Tab (Voice Recording & Waveform)
- **Waveform Canvas:** 100% width, 120px height canvas with dual-channel gradient visualization.
- **Action Button:** Circular 64px button transitioning from Indigo (`Record`) to Pulsing Crimson (`Stop`).
- **Live Timer:** Monospaced elapsed timer counter (`00:14.2`) centered below the visualizer.

### 4.3. Files Tab (Drag-and-Drop & Progress)
- **Dropzone:** Dashed 2px border with drag-over glow effect, supporting drag-and-drop or file browsing.
- **File Preview Card:** Displays file icon, filename, file size, and inline audio scrubber.
- **Sequential Progress Bar:** Multi-phase animated progress bar reflecting backend status:
  - Phase 1: Uploading & Preprocessing (10%–30%)
  - Phase 2: Whisper CPU Transcription (30%–90%)
  - Phase 3: Alignment & Export Generation (100%)

### 4.4. Audio-Synchronized Transcript Player
- **Header:** Audio player with scrub bar, speed control (`1x`, `1.25x`, `1.5x`, `2x`), word counter, and export menu (`TXT`, `SRT`, `VTT`, `JSON`).
- **Segment Chips:** Sentence blocks displaying clickable millisecond badges. Clicking jumps audio directly to the cue point.
- **Active Word Cueing:** Real-time highlighting follows playback position as the audio plays.
- **In-Page Search:** Search input with live hit highlighting and current match navigation (`1 of 4`).

### 4.5. Benchmark Analytics & Quality Explorer
- **Metric Cards:** 4-column metric grid displaying Overall WER (12.52%), CER (7.93%), Real-Time Factor (0.547 RTF), and Peak Memory.
- **Categorical Breakdown:** Horizontal progress bars illustrating condition performance (Clean: 5.75%, Technical: 2.02%, Cadence: 0.00%, Noise: 0.00%).
- **Interactive Dataset Table:** 50-sample table with category filter pills, search input, play buttons, and slide-out inspector drawer.
- **Slide-Out Inspection Drawer:** 460px right-hand drawer with backdrop overlay displaying audio waveforms, ground-truth reference, hypothesis text, and error breakdown.

---

## 5. Micro-Interactions & Animation Guidelines

1. **Button Hover & Press:**
   - Default: `transform: translateY(0); transition: all 0.15s ease;`
   - Hover: `transform: translateY(-1px); filter: brightness(1.1);`
   - Active: `transform: translateY(1px); filter: brightness(0.95);`
2. **Recording Pulse:** Crimson glow animation (`keyframes pulse-red`) expanding from 0 to 12px blur at 1.5s intervals.
3. **Drawer Transition:** Slide in from `translateX(100%)` to `translateX(0)` with `cubic-bezier(0.16, 1, 0.3, 1)` (300ms).
4. **Toast Notifications:** Float in from bottom-center, pause for 3000ms, and fade out smoothly.
