/**
 * Local Transcriber - Modern SaaS Application Controller
 * Aesthetic & UX inspired by Linear, ElevenLabs, and Descript
 * P0 Icon System, Audio ↔ Transcript Synchronization & Batch Queue
 */

// Canonical SVG Icon System (24x24 canvas, 1.75px stroke, round caps/joins, currentColor)
const ICONS = {
  mic: `<rect x="9" y="3.5" width="6" height="11" rx="3" /><path d="M6.5 11.5a5.5 5.5 0 0 0 11 0" /><path d="M12 17v3.5" /><path d="M9 20.5h6" />`,
  stop: `<rect x="7" y="7" width="10" height="10" rx="2.25" />`,
  play: `<path d="M9 6.5v11l9-5.5-9-5.5Z" />`,
  pause: `<rect x="7" y="6" width="3.5" height="12" rx="1.25" /><rect x="13.5" y="6" width="3.5" height="12" rx="1.25" />`,
  file: `<path d="M7 3.5h6l4 4v13H7z" /><path d="M13 3.5v4h4" /><path d="M9.5 12h5" /><path d="M9.5 15.5h5" />`,
  folder: `<path d="M3.5 7.5A2 2 0 0 1 5.5 5.5H10L12 7.5H18.5A2 2 0 0 1 20.5 9.5V17.5A2 2 0 0 1 18.5 19.5H5.5A2 2 0 0 1 3.5 17.5Z" />`,
  upload: `<path d="M12 15V4.5" /><path d="m8.5 8 3.5-3.5L15.5 8" /><path d="M5 13.5v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />`,
  check: `<path d="m5.5 12.5 4 4 9-9" />`,
  copy: `<rect x="8" y="8" width="11" height="11" rx="2" /><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" />`,
  download: `<path d="M12 3.5v11" /><path d="m8.5 11 3.5 3.5 3.5-3.5" /><path d="M5 17v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" />`,
  settings: `<circle cx="12" cy="12" r="3" /><path d="M19 13.5a7.5 7.5 0 0 0 0-3l1.7-1.2-2-3.4-1.9.8a7.7 7.7 0 0 0-2.6-1.5L14 3h-4l-.3 2.2A7.7 7.7 0 0 0 7.1 6.7L5.2 5.9l-2 3.4L5 10.5a7.5 7.5 0 0 0 0 3l-1.8 1.2 2 3.4 1.9-.8a7.7 7.7 0 0 0 2.6 1.5L10 21h4l.3-2.2a7.7 7.7 0 0 0 2.6-1.5l1.9.8 2-3.4Z" />`,
  analytics: `<path d="M5 19V10" /><path d="M12 19V5" /><path d="M19 19v-7" />`,
  chevronDown: `<path d="m7 9 5 5 5-5" />`,
  close: `<path d="m7 7 10 10" /><path d="m17 7-10 10" />`,
  search: `<circle cx="10.8" cy="10.8" r="5.8" /><path d="m15.2 15.2 4 4" />`
};

function getIconSvg(name, size = 18, extraClass = "") {
  const content = ICONS[name] || "";
  const isFilled = name === "play" || name === "pause";
  return `<svg class="svg-icon ${isFilled ? 'icon-filled' : ''} ${extraClass}" width="${size}" height="${size}" viewBox="0 0 24 24" ${isFilled ? 'fill="currentColor" stroke="none"' : 'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'}>${content}</svg>`;
}

// Global Application State
let mediaRecorder = null;
let audioChunks = [];
let audioContext = null;
let analyserNode = null;
let dataArray = null;
let animationFrameId = null;
let recordStartTime = 0;
let recordIntervalId = null;
let recordedBlob = null;
let currentDictationJobId = null;
let currentDictationSegments = [];

let currentFileJobId = null;
let currentFileSegments = [];
let selectedFile = null;
let batchQueue = [];
let isProcessingBatch = false;

let benchmarkData = [];
let activeCategoryFilter = "all";

// Active custom players
let dictationPlayerInstance = null;
let filePlayerInstance = null;
let activePlayerInstance = null;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupDictation();
  setupFileUpload();
  setupDropdowns();
  setupDrawer();
  setupSettings();
  setupKeyboardShortcuts();
  loadSystemInfo();
  loadBenchmarkData();
});

// Toast notification helper
function showToast(message) {
  const toast = document.getElementById("toastMessage");
  if (!toast) return;
  toast.innerText = message;
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 2200);
}

// Global Status Indicator Helper
function setGlobalStatus(statusText, isProcessing = false) {
  const el = document.getElementById("globalStatus");
  if (!el) return;
  el.innerText = statusText;
  const pill = el.parentElement;
  if (!pill) return;
  if (isProcessing) {
    pill.style.color = "#5b8cff";
    pill.style.background = "rgba(91, 140, 255, 0.08)";
    pill.style.borderColor = "rgba(91, 140, 255, 0.25)";
  } else {
    pill.style.color = "#34d399";
    pill.style.background = "rgba(52, 211, 153, 0.06)";
    pill.style.borderColor = "rgba(52, 211, 153, 0.18)";
  }
}

// Time formatter (00:00)
function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return "00:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// =============================================================
// Custom Audio Player Controller
// =============================================================
class CustomAudioPlayer {
  constructor({ audioElement, playBtn, currentTimeEl, durationEl, scrubberEl, speedGroupEl, onTimeUpdate }) {
    this.audio = audioElement;
    this.playBtn = playBtn;
    this.currentTimeEl = currentTimeEl;
    this.durationEl = durationEl;
    this.scrubber = scrubberEl;
    this.speedGroup = speedGroupEl;
    this.onTimeUpdate = onTimeUpdate;
    this.isSeeking = false;

    this.init();
  }

  init() {
    // Restore saved playback speed
    const savedSpeed = localStorage.getItem("transcriber.playbackRate") || "1";
    this.setSpeed(parseFloat(savedSpeed));

    // Play/Pause button
    if (this.playBtn) {
      this.playBtn.addEventListener("click", () => this.togglePlay());
    }

    // Audio events
    this.audio.addEventListener("play", () => {
      this.updatePlayBtnState(true);
      activePlayerInstance = this;
    });

    this.audio.addEventListener("pause", () => {
      this.updatePlayBtnState(false);
    });

    this.audio.addEventListener("ended", () => {
      this.updatePlayBtnState(false);
      if (this.scrubber) this.scrubber.value = 0;
      if (this.currentTimeEl) this.currentTimeEl.innerText = "00:00";
    });

    this.audio.addEventListener("loadedmetadata", () => {
      this.updateDuration();
    });

    this.audio.addEventListener("durationchange", () => {
      this.updateDuration();
    });

    this.audio.addEventListener("timeupdate", () => {
      if (!this.isSeeking) {
        this.updateTimeDisplay();
        if (this.audio.duration && this.scrubber) {
          this.scrubber.value = (this.audio.currentTime / this.audio.duration) * 100;
        }
      }
      if (this.onTimeUpdate) {
        this.onTimeUpdate(this.audio.currentTime);
      }
    });

    // Scrubber seek
    if (this.scrubber) {
      this.scrubber.addEventListener("input", () => {
        this.isSeeking = true;
        if (this.audio.duration && this.currentTimeEl) {
          const seekTime = (this.scrubber.value / 100) * this.audio.duration;
          this.currentTimeEl.innerText = formatTime(seekTime);
        }
      });
      this.scrubber.addEventListener("change", () => {
        if (this.audio.duration) {
          this.audio.currentTime = (this.scrubber.value / 100) * this.audio.duration;
        }
        this.isSeeking = false;
      });
    }

    // Speed selector pills
    if (this.speedGroup) {
      this.speedGroup.querySelectorAll(".speed-pill-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const speed = parseFloat(btn.getAttribute("data-speed"));
          this.setSpeed(speed);
        });
      });
    }
  }

  setSpeed(speed) {
    if (!speed) return;
    this.audio.playbackRate = speed;
    localStorage.setItem("transcriber.playbackRate", speed);
    if (this.speedGroup) {
      this.speedGroup.querySelectorAll(".speed-pill-btn").forEach((b) => {
        b.classList.toggle("active", parseFloat(b.getAttribute("data-speed")) === speed);
      });
    }
  }

  togglePlay() {
    if (!this.audio.src) return;
    if (this.audio.paused) {
      this.audio.play();
    } else {
      this.audio.pause();
    }
  }

  seekTo(seconds) {
    if (!this.audio.duration) return;
    this.audio.currentTime = Math.max(0, Math.min(seconds, this.audio.duration));
    if (this.audio.paused) {
      this.audio.play();
    }
  }

  updatePlayBtnState(isPlaying) {
    if (!this.playBtn) return;
    this.playBtn.innerHTML = isPlaying ? getIconSvg("pause", 16) : getIconSvg("play", 16);
  }

  updateTimeDisplay() {
    if (this.currentTimeEl) {
      this.currentTimeEl.innerText = formatTime(this.audio.currentTime);
    }
    if (this.durationEl && (!this.durationEl.innerText || this.durationEl.innerText === "00:00")) {
      this.updateDuration();
    }
  }

  updateDuration() {
    if (this.durationEl && this.audio.duration) {
      this.durationEl.innerText = formatTime(this.audio.duration);
    }
  }
}

// =============================================================
// Synchronized Segments & In-Page Search Manager
// =============================================================
function renderTranscriptSegments({ container, segments, onSegmentClick }) {
  container.innerHTML = "";
  if (!segments || segments.length === 0) {
    container.innerHTML = `<div style="padding: 16px; color: var(--text-tertiary); font-size: 13px;">No segment timestamps available for this audio.</div>`;
    return;
  }

  segments.forEach((seg, idx) => {
    const row = document.createElement("div");
    row.className = "segment-row";
    row.id = `${container.id}-seg-${idx}`;
    row.setAttribute("data-start", seg.start);
    row.setAttribute("data-end", seg.end);

    const timeBtn = document.createElement("button");
    timeBtn.className = "segment-timestamp-btn";
    timeBtn.innerHTML = `${getIconSvg("play", 10)} ${formatTime(seg.start)}`;
    timeBtn.title = `Jump to ${formatTime(seg.start)}`;

    const textEl = document.createElement("div");
    textEl.className = "segment-text";
    textEl.innerText = seg.text;

    row.appendChild(timeBtn);
    row.appendChild(textEl);

    row.addEventListener("click", () => {
      if (onSegmentClick) onSegmentClick(seg.start);
    });

    container.appendChild(row);
  });
}

function updateActiveSegment(container, currentTime) {
  const rows = container.querySelectorAll(".segment-row");
  let activeRow = null;

  rows.forEach((row) => {
    const start = parseFloat(row.getAttribute("data-start"));
    const end = parseFloat(row.getAttribute("data-end"));
    if (currentTime >= start && currentTime < end) {
      if (!row.classList.contains("active-segment")) {
        row.classList.add("active-segment");
        activeRow = row;
      }
    } else {
      row.classList.remove("active-segment");
    }
  });

  if (activeRow) {
    activeRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

function setupTranscriptSearch(searchInput, matchCountEl, segmentsContainer) {
  if (!searchInput || !segmentsContainer) return;

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase().trim();
    const rows = segmentsContainer.querySelectorAll(".segment-row");
    let matches = 0;

    rows.forEach((row) => {
      const textEl = row.querySelector(".segment-text");
      if (!textEl) return;
      const text = textEl.innerText;

      if (!query) {
        textEl.innerHTML = escapeHtml(text);
        row.style.display = "flex";
      } else {
        const lower = text.toLowerCase();
        if (lower.includes(query)) {
          matches++;
          row.style.display = "flex";
          const regex = new RegExp(`(${escapeRegExp(query)})`, "gi");
          textEl.innerHTML = escapeHtml(text).replace(regex, `<span class="search-highlight">$1</span>`);
        } else {
          row.style.display = "none";
        }
      }
    });

    if (matchCountEl) {
      if (query) {
        matchCountEl.style.display = "inline-block";
        matchCountEl.innerText = `${matches} match${matches === 1 ? '' : 'es'}`;
      } else {
        matchCountEl.style.display = "none";
      }
    }
  });
}

// -------------------------------------------------------------
// 1. Navigation Controller
// -------------------------------------------------------------
function setupNavigation() {
  const navTabs = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetTab = tab.getAttribute("data-tab");

      navTabs.forEach((t) => t.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      tab.classList.add("active");
      const activePane = document.getElementById(targetTab);
      if (activePane) activePane.classList.add("active");
    });
  });
}

// -------------------------------------------------------------
// 2. Dictate Screen (Capture + Real-time Waveform + Player + Sync)
// -------------------------------------------------------------
function setupDictation() {
  const recordBtn = document.getElementById("recordBtn");
  const pulseRing = document.getElementById("pulseRing");
  const recordTimer = document.getElementById("recordTimer");
  const recordStatus = document.getElementById("recordStatus");
  const canvasContainer = document.getElementById("canvasContainer");
  const canvas = document.getElementById("waveformCanvas");
  const canvasCtx = canvas ? canvas.getContext("2d") : null;

  const audioPreview = document.getElementById("dictationAudioPreview");
  const audioPlayer = document.getElementById("recordedAudioPlayer");
  const transcribeBtn = document.getElementById("transcribeRecordedBtn");

  const progressCard = document.getElementById("dictationProgress");
  const progressBar = document.getElementById("dictationProgressBar");
  const progressMsg = document.getElementById("dictationProgressMsg");
  const progressPct = document.getElementById("dictationProgressPct");

  const resultBox = document.getElementById("dictationResultBox");
  const textarea = document.getElementById("dictationTextarea");
  const segmentsList = document.getElementById("dictationSegmentsList");
  const wordCount = document.getElementById("dictationWordCount");
  const charCount = document.getElementById("dictationCharCount");
  const rtfBadge = document.getElementById("dictationRtfBadge");

  const tabSegments = document.getElementById("dictationTabSegments");
  const tabEditor = document.getElementById("dictationTabEditor");
  const searchInput = document.getElementById("dictationSearchInput");
  const matchCount = document.getElementById("dictationMatchCount");

  // Initialize Custom Audio Player for Dictation
  dictationPlayerInstance = new CustomAudioPlayer({
    audioElement: audioPlayer,
    playBtn: document.getElementById("dictationPlayBtn"),
    currentTimeEl: document.getElementById("dictationCurrentTime"),
    durationEl: document.getElementById("dictationDuration"),
    scrubberEl: document.getElementById("dictationScrubber"),
    speedGroupEl: document.getElementById("dictationSpeedGroup"),
    onTimeUpdate: (currTime) => {
      updateActiveSegment(segmentsList, currTime);
    }
  });

  // Setup View Toggle (Segments vs Editor)
  tabSegments.addEventListener("click", () => {
    tabSegments.classList.add("active");
    tabEditor.classList.remove("active");
    segmentsList.style.display = "flex";
    textarea.style.display = "none";
  });

  tabEditor.addEventListener("click", () => {
    tabEditor.classList.add("active");
    tabSegments.classList.remove("active");
    textarea.style.display = "block";
    segmentsList.style.display = "none";
  });

  setupTranscriptSearch(searchInput, matchCount, segmentsList);

  let isRecording = false;

  recordBtn.addEventListener("click", async () => {
    if (!isRecording) {
      // Start Recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        analyserNode = audioContext.createAnalyser();
        analyserNode.fftSize = 256;
        source.connect(analyserNode);

        const bufferLength = analyserNode.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          recordedBlob = new Blob(audioChunks, { type: "audio/webm" });
          const audioUrl = URL.createObjectURL(recordedBlob);
          audioPlayer.src = audioUrl;
          audioPlayer.load();
          audioPreview.style.display = "flex";
          recordStatus.innerText = "Voice captured. Ready to transcribe.";
          setGlobalStatus("Ready", false);
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add("recording");
        pulseRing.classList.add("active");
        recordBtn.innerHTML = getIconSvg("stop", 30);
        recordStatus.innerText = "Recording... Speak clearly";
        setGlobalStatus("Recording", true);
        canvasContainer.classList.add("active");
        audioPreview.style.display = "none";
        resultBox.style.display = "none";

        // Timer
        recordStartTime = Date.now();
        recordIntervalId = setInterval(() => {
          const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
          const mins = String(Math.floor(elapsed / 60)).padStart(2, "0");
          const secs = String(elapsed % 60).padStart(2, "0");
          recordTimer.innerText = `${mins}:${secs}`;
        }, 500);

        // Waveform Visualizer
        function drawWaveform() {
          if (!isRecording || !canvasCtx) return;
          animationFrameId = requestAnimationFrame(drawWaveform);
          analyserNode.getByteFrequencyData(dataArray);

          canvasCtx.fillStyle = "#090c12";
          canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

          const barWidth = (canvas.width / bufferLength) * 2.2;
          let x = 0;

          const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, 0);
          gradient.addColorStop(0, "#5b8cff");
          gradient.addColorStop(1, "#38bdf8");

          for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * canvas.height * 0.9;
            canvasCtx.fillStyle = gradient;
            canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
            x += barWidth + 1;
          }
        }
        drawWaveform();

      } catch (err) {
        alert("Microphone access denied: " + err.message);
      }
    } else {
      // Stop Recording
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
      }
      isRecording = false;
      recordBtn.classList.remove("recording");
      pulseRing.classList.remove("active");
      recordBtn.innerHTML = getIconSvg("mic", 28);
      clearInterval(recordIntervalId);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      canvasContainer.classList.remove("active");
    }
  });

  // Transcribe Recorded Voice Clip
  transcribeBtn.addEventListener("click", async () => {
    if (!recordedBlob) return;

    progressCard.style.display = "block";
    progressBar.style.width = "15%";
    progressPct.innerText = "15%";
    progressMsg.innerText = "Initializing speech recognition...";
    resultBox.style.display = "none";
    setGlobalStatus("Transcribing", true);

    const formData = new FormData();
    formData.append("file", recordedBlob, "dictation.webm");
    formData.append("model", "small");
    formData.append("language", "en");

    try {
      const res = await fetch("/api/record", { method: "POST", body: formData });
      const data = await res.json();
      currentDictationJobId = data.job_id;

      pollJob(currentDictationJobId, (job) => {
        progressBar.style.width = `${job.progress}%`;
        progressPct.innerText = `${job.progress}%`;
        progressMsg.innerText = job.message;

        if (job.status === "COMPLETED") {
          progressCard.style.display = "none";
          resultBox.style.display = "flex";
          const resObj = job.result || {};
          textarea.value = resObj.text || "";
          currentDictationSegments = resObj.segments || [];

          // Render Synced Segments
          renderTranscriptSegments({
            container: segmentsList,
            segments: currentDictationSegments,
            onSegmentClick: (timeSec) => dictationPlayerInstance.seekTo(timeSec)
          });

          updateCounts(textarea, wordCount, charCount);
          rtfBadge.innerText = `${resObj.rtf || 0}× Real-Time (${resObj.latency || 0}s)`;
          setGlobalStatus("Ready", false);
          showToast("Transcription complete");
        } else if (job.status === "FAILED") {
          progressCard.style.display = "none";
          setGlobalStatus("Ready", false);
          alert(job.message || "Transcription failed");
        }
      });
    } catch (err) {
      alert("Error submitting recording: " + err.message);
      progressCard.style.display = "none";
      setGlobalStatus("Ready", false);
    }
  });

  // Copy to clipboard
  document.getElementById("copyDictationBtn").addEventListener("click", () => {
    navigator.clipboard.writeText(textarea.value);
    showToast("Copied to clipboard");
  });

  // Wire exports
  setupExportActions("dictation", () => currentDictationJobId, () => textarea.value);
  textarea.addEventListener("input", () => updateCounts(textarea, wordCount, charCount));
}

// -------------------------------------------------------------
// 3. Audio Files Drag & Drop + Batch Queue Transcriber
// -------------------------------------------------------------
function setupFileUpload() {
  const dropzone = document.getElementById("fileDropzone");
  const fileInput = document.getElementById("fileInput");
  const card = document.getElementById("fileSelectedCard");
  const fileName = document.getElementById("selectedFileName");
  const fileSize = document.getElementById("selectedFileSize");
  const player = document.getElementById("fileAudioPlayer");
  const clearBtn = document.getElementById("clearFileBtn");
  const startBtn = document.getElementById("startFileTranscribeBtn");
  const modelSelect = document.getElementById("fileModelSelect");
  const langSelect = document.getElementById("fileLangSelect");

  const progressCard = document.getElementById("fileProgressCard");
  const progressBar = document.getElementById("fileProgressBar");
  const progressMsg = document.getElementById("fileProgressMsg");
  const progressPct = document.getElementById("fileProgressPct");

  const resultBox = document.getElementById("fileResultBox");
  const textarea = document.getElementById("fileTextarea");
  const segmentsList = document.getElementById("fileSegmentsList");
  const wordCount = document.getElementById("fileWordCount");
  const charCount = document.getElementById("fileCharCount");
  const rtfBadge = document.getElementById("fileRtfBadge");

  const tabSegments = document.getElementById("fileTabSegments");
  const tabEditor = document.getElementById("fileTabEditor");
  const searchInput = document.getElementById("fileSearchInput");
  const matchCount = document.getElementById("fileMatchCount");

  // Initialize Custom Audio Player for Files
  filePlayerInstance = new CustomAudioPlayer({
    audioElement: player,
    playBtn: document.getElementById("filePlayBtn"),
    currentTimeEl: document.getElementById("fileCurrentTime"),
    durationEl: document.getElementById("fileDuration"),
    scrubberEl: document.getElementById("fileScrubber"),
    speedGroupEl: document.getElementById("fileSpeedGroup"),
    onTimeUpdate: (currTime) => {
      updateActiveSegment(segmentsList, currTime);
    }
  });

  // View mode switcher
  tabSegments.addEventListener("click", () => {
    tabSegments.classList.add("active");
    tabEditor.classList.remove("active");
    segmentsList.style.display = "flex";
    textarea.style.display = "none";
  });

  tabEditor.addEventListener("click", () => {
    tabEditor.classList.add("active");
    tabSegments.classList.remove("active");
    textarea.style.display = "block";
    segmentsList.style.display = "none";
  });

  setupTranscriptSearch(searchInput, matchCount, segmentsList);

  // Dropzone click triggers hidden file input
  dropzone.addEventListener("click", (e) => {
    if (e.target.tagName !== "INPUT") {
      fileInput.click();
    }
  });

  // Drag-and-drop feedback
  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragging");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragging");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (e.dataTransfer.files.length === 1) {
        handleSingleFile(e.dataTransfer.files[0]);
      } else {
        handleBatchFiles(e.dataTransfer.files);
      }
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      if (e.target.files.length === 1) {
        handleSingleFile(e.target.files[0]);
      } else {
        handleBatchFiles(e.target.files);
      }
    }
  });

  function handleSingleFile(file) {
    selectedFile = file;
    fileName.innerText = file.name;
    fileSize.innerText = (file.size / (1024 * 1024)).toFixed(2) + " MB";
    player.src = URL.createObjectURL(file);
    player.load();
    card.style.display = "block";
    resultBox.style.display = "none";
  }

  function handleBatchFiles(files) {
    const batchCard = document.getElementById("batchQueueCard");
    const countEl = document.getElementById("batchQueueCount");
    batchCard.style.display = "block";

    Array.from(files).forEach((file) => {
      const item = {
        id: Math.random().toString(36).substring(2, 9),
        file: file,
        name: file.name,
        size: (file.size / (1024 * 1024)).toFixed(2) + " MB",
        status: "queued",
        progress: 0,
        jobId: null,
        result: null
      };
      batchQueue.push(item);
    });

    countEl.innerText = `${batchQueue.length} files`;
    renderBatchQueue();
    processBatchQueue();
  }

  function renderBatchQueue() {
    const list = document.getElementById("batchQueueList");
    if (!list) return;
    list.innerHTML = "";

    batchQueue.forEach((item) => {
      const row = document.createElement("div");
      row.className = `batch-item-row ${item.status === 'processing' ? 'active' : ''}`;
      row.id = `batch-${item.id}`;

      let badgeHtml = "";
      if (item.status === "queued") {
        badgeHtml = `<span class="batch-status-badge batch-status-queued">Queued</span>`;
      } else if (item.status === "processing") {
        badgeHtml = `<span class="batch-status-badge batch-status-processing">Processing (${item.progress}%)</span>`;
      } else if (item.status === "complete") {
        badgeHtml = `<span class="batch-status-badge batch-status-complete">${getIconSvg("check", 12)} Complete</span>`;
      } else {
        badgeHtml = `<span class="batch-status-badge batch-status-failed">Failed</span>`;
      }

      row.innerHTML = `
        <div class="batch-item-info">
          <div class="batch-item-name">${escapeHtml(item.name)}</div>
          <div class="batch-item-meta">${item.size}</div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          ${badgeHtml}
          ${item.status === 'complete' ? `<button class="btn-outline" style="height: 26px; padding: 0 8px; font-size: 11px;" onclick="loadBatchItemTranscript('${item.id}')">View</button>` : ''}
        </div>
      `;

      list.appendChild(row);
    });
  }

  window.loadBatchItemTranscript = function(id) {
    const item = batchQueue.find(b => b.id === id);
    if (!item || !item.result) return;

    selectedFile = item.file;
    fileName.innerText = item.name;
    fileSize.innerText = item.size;
    player.src = URL.createObjectURL(item.file);
    player.load();
    card.style.display = "block";

    resultBox.style.display = "flex";
    currentFileJobId = item.jobId;
    textarea.value = item.result.text || "";
    currentFileSegments = item.result.segments || [];

    renderTranscriptSegments({
      container: segmentsList,
      segments: currentFileSegments,
      onSegmentClick: (timeSec) => filePlayerInstance.seekTo(timeSec)
    });

    updateCounts(textarea, wordCount, charCount);
    rtfBadge.innerText = `${item.result.rtf || 0}× Real-Time (${item.result.latency || 0}s)`;
    showToast(`Loaded ${item.name}`);
  };

  async function processBatchQueue() {
    if (isProcessingBatch) return;
    const nextItem = batchQueue.find(b => b.status === "queued");
    if (!nextItem) return;

    isProcessingBatch = true;
    nextItem.status = "processing";
    nextItem.progress = 10;
    renderBatchQueue();
    setGlobalStatus(`Transcribing batch...`, true);

    const formData = new FormData();
    formData.append("file", nextItem.file);
    formData.append("model", modelSelect.value);
    formData.append("language", langSelect.value);

    try {
      const res = await fetch("/api/transcribe", { method: "POST", body: formData });
      const data = await res.json();
      nextItem.jobId = data.job_id;

      pollJob(nextItem.jobId, (job) => {
        nextItem.progress = job.progress;
        renderBatchQueue();

        if (job.status === "COMPLETED") {
          nextItem.status = "complete";
          nextItem.result = job.result;
          renderBatchQueue();
          isProcessingBatch = false;
          processBatchQueue();
        } else if (job.status === "FAILED") {
          nextItem.status = "failed";
          renderBatchQueue();
          isProcessingBatch = false;
          processBatchQueue();
        }
      });
    } catch (err) {
      nextItem.status = "failed";
      renderBatchQueue();
      isProcessingBatch = false;
      processBatchQueue();
    }
  }

  clearBtn.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    card.style.display = "none";
    player.src = "";
    resultBox.style.display = "none";
  });

  startBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    progressCard.style.display = "block";
    progressBar.style.width = "10%";
    progressPct.innerText = "10%";
    progressMsg.innerText = "Submitting audio file to Whisper...";
    resultBox.style.display = "none";
    setGlobalStatus("Transcribing", true);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("model", modelSelect.value);
    formData.append("language", langSelect.value);

    try {
      const res = await fetch("/api/transcribe", { method: "POST", body: formData });
      const data = await res.json();
      currentFileJobId = data.job_id;

      pollJob(currentFileJobId, (job) => {
        progressBar.style.width = `${job.progress}%`;
        progressPct.innerText = `${job.progress}%`;
        progressMsg.innerText = job.message;

        if (job.status === "COMPLETED") {
          progressCard.style.display = "none";
          resultBox.style.display = "flex";
          const resObj = job.result || {};
          textarea.value = resObj.text || "";
          currentFileSegments = resObj.segments || [];

          // Render Synced Segments
          renderTranscriptSegments({
            container: segmentsList,
            segments: currentFileSegments,
            onSegmentClick: (timeSec) => filePlayerInstance.seekTo(timeSec)
          });

          updateCounts(textarea, wordCount, charCount);
          rtfBadge.innerText = `${resObj.rtf || 0}× Real-Time (${resObj.latency || 0}s)`;
          setGlobalStatus("Ready", false);
          showToast("Transcription complete");
        } else if (job.status === "FAILED") {
          progressCard.style.display = "none";
          setGlobalStatus("Ready", false);
          alert(job.message || "Transcription failed");
        }
      });
    } catch (err) {
      alert("Error uploading file: " + err.message);
      progressCard.style.display = "none";
      setGlobalStatus("Ready", false);
    }
  });

  document.getElementById("copyFileBtn").addEventListener("click", () => {
    navigator.clipboard.writeText(textarea.value);
    showToast("Copied to clipboard");
  });

  setupExportActions("file", () => currentFileJobId, () => textarea.value);
  textarea.addEventListener("input", () => updateCounts(textarea, wordCount, charCount));
}

// -------------------------------------------------------------
// 4. Job Polling Service
// -------------------------------------------------------------
function pollJob(jobId, callback) {
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`/api/jobs/${jobId}`);
      if (!res.ok) return;
      const job = await res.json();
      callback(job);

      if (job.status === "COMPLETED" || job.status === "FAILED" || job.status === "CANCELLED") {
        clearInterval(interval);
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 600);
}

function updateCounts(textarea, wordEl, charEl) {
  const text = textarea.value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  wordEl.innerText = `${words} words`;
  charEl.innerText = `${text.length} chars`;
}

// -------------------------------------------------------------
// 5. Dropdown Menu Handler
// -------------------------------------------------------------
function setupDropdowns() {
  const dictMenuBtn = document.getElementById("exportDictationMenuBtn");
  const dictMenu = document.getElementById("exportDictationMenu");
  const fileMenuBtn = document.getElementById("exportFileMenuBtn");
  const fileMenu = document.getElementById("exportFileMenu");

  dictMenuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    dictMenu.classList.toggle("show");
    fileMenu.classList.remove("show");
  });

  fileMenuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileMenu.classList.toggle("show");
    dictMenu.classList.remove("show");
  });

  document.addEventListener("click", () => {
    dictMenu.classList.remove("show");
    fileMenu.classList.remove("show");
  });
}

function setupExportActions(prefix, getJobId, getText) {
  const formats = [
    { id: "Txt", ext: "txt" },
    { id: "Srt", ext: "srt" },
    { id: "Vtt", ext: "vtt" },
    { id: "Json", ext: "json" }
  ];

  formats.forEach(({ id, ext }) => {
    const el = document.getElementById(`export${prefix.charAt(0).toUpperCase() + prefix.slice(1)}${id}`);
    if (!el) return;
    el.addEventListener("click", () => {
      const jobId = getJobId();
      if (!jobId) {
        downloadLocalFile(`transcript.${ext}`, getText());
        return;
      }
      window.location.href = `/api/jobs/${jobId}/export/${ext}`;
    });
  });
}

function downloadLocalFile(filename, text) {
  const element = document.createElement("a");
  element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text));
  element.setAttribute("download", filename);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

// -------------------------------------------------------------
// 6. Quality & Benchmark Explorer + Slide-out Drawer
// -------------------------------------------------------------
async function loadBenchmarkData() {
  const tbody = document.getElementById("benchmarkTbody");
  const searchInput = document.getElementById("benchmarkSearch");
  const filterBtns = document.querySelectorAll(".filter-btn");

  if (!tbody) return;

  try {
    const res = await fetch("/api/benchmark");
    const data = await res.json();
    benchmarkData = data.samples || [];
    applyBenchmarkFilters();

    // Category Filter Pills
    filterBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        filterBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeCategoryFilter = btn.getAttribute("data-category");
        applyBenchmarkFilters();
      });
    });

    // Search Query
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        applyBenchmarkFilters();
      });
    }
  } catch (err) {
    console.error("Failed to load benchmark data:", err);
  }
}

function applyBenchmarkFilters() {
  const searchInput = document.getElementById("benchmarkSearch");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

  const filtered = benchmarkData.filter((item) => {
    const cat = (item.category || "").toLowerCase();
    let catMatch = true;
    if (activeCategoryFilter === "clean") {
      catMatch = cat.includes("clean");
    } else if (activeCategoryFilter === "noise") {
      catMatch = cat.includes("noise") || cat.includes("acoustic");
    } else if (activeCategoryFilter === "technical") {
      catMatch = cat.includes("technical");
    } else if (activeCategoryFilter === "conversational") {
      catMatch = cat.includes("conversational");
    } else if (activeCategoryFilter === "rates") {
      catMatch = cat.includes("rate") || cat.includes("cadence") || cat.includes("fast") || cat.includes("slow");
    } else if (activeCategoryFilter === "numeric") {
      catMatch = cat.includes("numeric");
    }

    const textMatch = !query || 
      (item.audio_file || "").toLowerCase().includes(query) ||
      (item.category || "").toLowerCase().includes(query) ||
      (item.reference || "").toLowerCase().includes(query) ||
      (item.hypothesis || "").toLowerCase().includes(query);

    return catMatch && textMatch;
  });

  renderBenchmarkRows(filtered);
}

function renderBenchmarkRows(samples) {
  const tbody = document.getElementById("benchmarkTbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  samples.forEach((s) => {
    const tr = document.createElement("tr");

    const werVal = parseFloat(s.wer);
    const werPercent = isNaN(werVal) ? "N/A" : (werVal * 100).toFixed(1) + "%";
    
    let tagClass = "tag-good";
    if (!isNaN(werVal)) {
      if (werVal === 0) tagClass = "tag-excellent";
      else if (werVal >= 0.2) tagClass = "tag-warning";
    }

    tr.innerHTML = `
      <td>
        <button class="play-sm-btn" onclick="event.stopPropagation(); playBenchmarkAudio('${s.audio_file}')" title="Play audio">
          ${getIconSvg("play", 13)}
        </button>
      </td>
      <td><span style="font-family: var(--font-mono); font-size: 12px; font-weight: 500;">${escapeHtml(s.audio_file)}</span></td>
      <td><span style="font-size: 11px; padding: 2px 7px; border-radius: 9999px; background: rgba(255,255,255,0.04); color: var(--text-secondary);">${escapeHtml(s.category || 'Standard')}</span></td>
      <td style="font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary);">${s.duration_sec}s</td>
      <td><span class="tag-badge ${tagClass}">${werPercent}</span></td>
      <td style="font-family: var(--font-mono); font-size: 12px; color: var(--accent);">${s.rtf_factor}×</td>
      <td>
        <button class="btn-outline" style="height: 26px; padding: 0 8px; font-size: 11px;" onclick="event.stopPropagation(); openDrawerForSample('${s.audio_file}')">
          View
        </button>
      </td>
    `;

    tr.addEventListener("click", () => {
      openDrawerForSample(s.audio_file);
    });

    tbody.appendChild(tr);
  });
}

let activeBenchmarkAudio = null;
window.playBenchmarkAudio = function(filename) {
  if (activeBenchmarkAudio) {
    activeBenchmarkAudio.pause();
    activeBenchmarkAudio = null;
  }
  activeBenchmarkAudio = new Audio(`/api/audio/${filename}`);
  activeBenchmarkAudio.play();
  showToast(`Playing ${filename}`);
};

// -------------------------------------------------------------
// 7. Slide-over Benchmark Detail Drawer
// -------------------------------------------------------------
function setupDrawer() {
  const backdrop = document.getElementById("drawerBackdrop");
  const drawer = document.getElementById("benchmarkDrawer");
  const closeBtn = document.getElementById("drawerCloseBtn");

  function closeDrawer() {
    backdrop.classList.remove("active");
    drawer.classList.remove("active");
    document.body.style.overflow = "";
    const player = document.getElementById("drawerAudioPlayer");
    if (player) player.pause();
  }

  backdrop.addEventListener("click", closeDrawer);
  closeBtn.addEventListener("click", closeDrawer);
}

window.openDrawerForSample = function(filename) {
  const sample = benchmarkData.find((s) => s.audio_file === filename);
  if (!sample) return;

  const backdrop = document.getElementById("drawerBackdrop");
  const drawer = document.getElementById("benchmarkDrawer");

  document.getElementById("drawerSampleTitle").innerText = sample.audio_file;
  document.getElementById("drawerCategory").innerText = sample.category || "Standard";
  document.getElementById("drawerDuration").innerText = `${sample.duration_sec}s`;
  
  const werVal = parseFloat(sample.wer);
  const werPercent = isNaN(werVal) ? "N/A" : (werVal * 100).toFixed(1) + "%";
  document.getElementById("drawerWer").innerText = werPercent;
  document.getElementById("drawerRtf").innerText = `${sample.rtf_factor}× Real-Time`;

  const player = document.getElementById("drawerAudioPlayer");
  player.src = `/api/audio/${sample.audio_file}`;

  document.getElementById("drawerReferenceText").innerText = sample.reference || "";
  document.getElementById("drawerHypothesisText").innerText = sample.hypothesis || "";

  document.body.style.overflow = "hidden";
  backdrop.classList.add("active");
  drawer.classList.add("active");
};

// -------------------------------------------------------------
// 8. Settings & System Host Information
// -------------------------------------------------------------
async function loadSystemInfo() {
  try {
    const res = await fetch("/api/system");
    const data = await res.json();

    document.getElementById("sysOs").innerText = data.os === "win32" ? "Windows Desktop" : data.os;
    document.getElementById("sysCores").innerText = `${data.cpu_count} Logical Cores`;
    document.getElementById("sysRam").innerText = `${data.ram_available_gb} GB / ${data.ram_total_gb} GB`;
    document.getElementById("sysProcRam").innerText = `${data.process_ram_mb} MB`;

    document.getElementById("settingsModel").value = data.active_model;
    const threadEl = document.getElementById("settingsThreads");
    if (threadEl && data.configured_threads) {
      const exists = Array.from(threadEl.options).some(o => o.value == data.configured_threads);
      if (!exists) {
        const opt = document.createElement("option");
        opt.value = data.configured_threads;
        opt.innerText = `${data.configured_threads} Threads`;
        threadEl.appendChild(opt);
      }
      threadEl.value = data.configured_threads;
    }
  } catch (err) {
    console.error("Error loading system info:", err);
  }
}

function setupSettings() {
  const saveBtn = document.getElementById("saveSettingsBtn");
  if (!saveBtn) return;

  saveBtn.addEventListener("click", async () => {
    const model = document.getElementById("settingsModel").value;
    const threads = parseInt(document.getElementById("settingsThreads").value, 10);

    saveBtn.innerText = "Applying...";
    saveBtn.disabled = true;

    try {
      const res = await fetch("/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, threads })
      });
      const data = await res.json();
      showToast(`Settings saved: ${data.model.toUpperCase()}`);
      loadSystemInfo();
    } catch (err) {
      alert("Failed to update settings: " + err.message);
    } finally {
      saveBtn.innerText = "Save Settings";
      saveBtn.disabled = false;
    }
  });
}

// -------------------------------------------------------------
// 9. Keyboard Shortcuts System
// -------------------------------------------------------------
function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Check if user is typing in form controls
    const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName) || e.target.isContentEditable;

    if (isTyping) {
      if (e.key === "Escape") {
        e.target.blur();
      }
      return;
    }

    // Space: Toggle Play/Pause on active audio player (or recording if dictation pane is active and ready)
    if (e.code === "Space") {
      e.preventDefault();
      if (activePlayerInstance && activePlayerInstance.audio && activePlayerInstance.audio.src) {
        activePlayerInstance.togglePlay();
      } else {
        const activeTab = document.querySelector(".nav-tab.active");
        if (activeTab && activeTab.getAttribute("data-tab") === "tab-dictation") {
          document.getElementById("recordBtn").click();
        }
      }
      return;
    }

    // Escape: Close drawer or clear search
    if (e.key === "Escape") {
      const backdrop = document.getElementById("drawerBackdrop");
      const drawer = document.getElementById("benchmarkDrawer");
      if (drawer && drawer.classList.contains("active")) {
        backdrop.classList.remove("active");
        drawer.classList.remove("active");
        document.body.style.overflow = "";
        const player = document.getElementById("drawerAudioPlayer");
        if (player) player.pause();
      }
      return;
    }

    // Seek Audio (ArrowLeft / ArrowRight)
    if (e.code === "ArrowLeft" && activePlayerInstance && activePlayerInstance.audio && activePlayerInstance.audio.src) {
      e.preventDefault();
      const jump = e.shiftKey ? 5 : 2;
      activePlayerInstance.seekTo(activePlayerInstance.audio.currentTime - jump);
      return;
    }
    if (e.code === "ArrowRight" && activePlayerInstance && activePlayerInstance.audio && activePlayerInstance.audio.src) {
      e.preventDefault();
      const jump = e.shiftKey ? 5 : 2;
      activePlayerInstance.seekTo(activePlayerInstance.audio.currentTime + jump);
      return;
    }

    // Ctrl/Cmd + C: Copy active transcript if no text selection
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "c") {
      if (!window.getSelection().toString()) {
        const activeTab = document.querySelector(".nav-tab.active");
        let copyText = "";
        if (activeTab && activeTab.getAttribute("data-tab") === "tab-dictation") {
          copyText = document.getElementById("dictationTextarea").value;
        } else {
          copyText = document.getElementById("fileTextarea").value;
        }
        if (copyText) {
          navigator.clipboard.writeText(copyText);
          showToast("Copied transcript to clipboard");
        }
      }
      return;
    }

    // Ctrl/Cmd + F: Quick focus transcript search
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
      const activeTab = document.querySelector(".nav-tab.active");
      let searchInput = null;
      if (activeTab && activeTab.getAttribute("data-tab") === "tab-dictation") {
        searchInput = document.getElementById("dictationSearchInput");
      } else if (activeTab && activeTab.getAttribute("data-tab") === "tab-files") {
        searchInput = document.getElementById("fileSearchInput");
      }
      if (searchInput && searchInput.offsetParent !== null) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
      return;
    }
  });
}
