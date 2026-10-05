"""
transcribe.py
Offline Speech-to-Text inference script using OpenAI Whisper.
Transcribes audio files, profiles CPU time, latency, Real-Time Factor (RTF), and memory usage.
Calculates Word Error Rate (WER) and Character Error Rate (CER) per sample when ground truth is provided.
"""

import os
import sys
import time
import argparse
import glob
import re
import string
import csv
import psutil
import soundfile as sf
import torch
import whisper
from tqdm import tqdm
from jiwer import wer, cer

# Normalize text for standardized WER/CER comparison
def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Lowercase
    text = text.lower().strip()
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_audio_duration(file_path: str) -> float:
    try:
        info = sf.info(file_path)
        return float(info.duration)
    except Exception:
        return 0.0


def load_references(transcripts_path: str) -> dict:
    """Load ground-truth reference transcripts from CSV or directory of .txt files."""
    references = {}
    if not transcripts_path or not os.path.exists(transcripts_path):
        return references

    if os.path.isfile(transcripts_path):
        # CSV file
        with open(transcripts_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Match by filename or base id
                fname = row.get("filename") or row.get("id") or row.get("audio_file")
                ref = row.get("reference_transcript") or row.get("transcript") or row.get("text")
                if fname and ref:
                    base_key = os.path.splitext(os.path.basename(fname))[0]
                    references[base_key] = ref.strip()
    elif os.path.isdir(transcripts_path):
        # Check for transcripts.csv inside dir
        csv_candidate = os.path.join(transcripts_path, "transcripts.csv")
        if os.path.exists(csv_candidate):
            return load_references(csv_candidate)

        # Or read individual .txt files
        for txt_file in glob.glob(os.path.join(transcripts_path, "*.txt")):
            base_key = os.path.splitext(os.path.basename(txt_file))[0]
            with open(txt_file, "r", encoding="utf-8") as f:
                references[base_key] = f.read().strip()

    return references


def main():
    parser = argparse.ArgumentParser(description="Local Offline Speech-to-Text Transcription with Whisper")
    parser.add_argument("audio_dir", nargs="?", default="audio_samples", help="Path to audio files directory or single audio file")
    parser.add_argument("transcripts", nargs="?", default="transcripts", help="Path to reference transcripts directory or CSV")
    parser.add_argument("output_csv", nargs="?", default="results.csv", help="Path to output CSV results file")
    parser.add_argument("--model", "-m", default="base", choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "turbo"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--threads", "-t", type=int, default=os.cpu_count(), help="Number of CPU threads to use")
    parser.add_argument("--device", "-d", default="cpu", choices=["cpu", "cuda"], help="Inference device (default: cpu)")
    parser.add_argument("--fp16", action="store_true", help="Use fp16 (only on GPU)")

    args = parser.parse_args()

    # Configure CPU threading
    if args.device == "cpu":
        torch.set_num_threads(args.threads)
        print(f"Configured CPU execution with {args.threads} threads.")

    # Locate audio files
    if os.path.isfile(args.audio_dir):
        audio_files = [args.audio_dir]
    elif os.path.isdir(args.audio_dir):
        patterns = [os.path.join(args.audio_dir, "*.wav"), os.path.join(args.audio_dir, "*.mp3"), os.path.join(args.audio_dir, "*.flac")]
        audio_files = []
        for p in patterns:
            audio_files.extend(glob.glob(p))
        audio_files.sort()
    else:
        print(f"Error: Audio directory/file not found: {args.audio_dir}")
        sys.exit(1)

    if not audio_files:
        print(f"Error: No audio files found in {args.audio_dir}")
        sys.exit(1)

    # Load ground-truth transcripts
    references = load_references(args.transcripts)
    print(f"Loaded {len(references)} reference transcripts for evaluation.")

    # Initialize model
    print(f"\nLoading Whisper model '{args.model}' on {args.device}...")
    load_start = time.perf_counter()
    model = whisper.load_model(args.model, device=args.device)
    load_time = time.perf_counter() - load_start
    print(f"Model loaded successfully in {load_time:.2f} seconds.")

    process = psutil.Process()
    results = []
    total_audio_sec = 0.0
    total_wall_sec = 0.0
    total_cpu_sec = 0.0

    print(f"\nTranscribing {len(audio_files)} audio samples...")
    pbar = tqdm(audio_files, desc="Inference", unit="sample")

    for audio_path in pbar:
        filename = os.path.basename(audio_path)
        base_id = os.path.splitext(filename)[0]
        duration = get_audio_duration(audio_path)
        total_audio_sec += duration

        # Reference transcript
        ref_text = references.get(base_id, "")

        # Profile memory before
        mem_before = process.memory_info().rss / (1024 * 1024)

        # Transcribe & profile
        cpu_start = time.process_time()
        wall_start = time.perf_counter()

        transcribe_result = model.transcribe(
            audio_path,
            language=args.language,
            fp16=(args.device == "cuda" and args.fp16),
            verbose=False
        )

        wall_time = time.perf_counter() - wall_start
        cpu_time = time.process_time() - cpu_start
        mem_after = process.memory_info().rss / (1024 * 1024)

        total_wall_sec += wall_time
        total_cpu_sec += cpu_time

        hyp_text = transcribe_result.get("text", "").strip()

        # Real-time factor (audio duration / elapsed wall time)
        rtf = (duration / wall_time) if wall_time > 0 else 0.0

        # Compute WER & CER if reference is available
        norm_ref = normalize_text(ref_text)
        norm_hyp = normalize_text(hyp_text)

        if norm_ref:
            try:
                sample_wer = round(wer(norm_ref, norm_hyp), 4)
                sample_cer = round(cer(norm_ref, norm_hyp), 4)
            except Exception:
                sample_wer = 0.0
                sample_cer = 0.0
        else:
            sample_wer = None
            sample_cer = None

        row = {
            "audio_file": filename,
            "duration_sec": round(duration, 2),
            "reference": ref_text,
            "hypothesis": hyp_text,
            "wer": sample_wer if sample_wer is not None else "N/A",
            "cer": sample_cer if sample_cer is not None else "N/A",
            "latency_sec": round(wall_time, 3),
            "cpu_time_sec": round(cpu_time, 3),
            "rtf_factor": round(rtf, 2),
            "memory_rss_mb": round(mem_after, 1)
        }
        results.append(row)

        pbar.set_postfix({"RTF": f"{rtf:.1f}x", "WER": f"{sample_wer:.2f}" if sample_wer is not None else "N/A"})

    # Ensure output dir exists
    out_dir = os.path.dirname(args.output_csv)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Save to CSV
    fieldnames = [
        "audio_file", "duration_sec", "reference", "hypothesis",
        "wer", "cer", "latency_sec", "cpu_time_sec", "rtf_factor", "memory_rss_mb"
    ]
    with open(args.output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nTranscription complete! Results saved to: {os.path.abspath(args.output_csv)}")

    # Overall summary
    avg_rtf = total_audio_sec / total_wall_sec if total_wall_sec > 0 else 0.0
    valid_wers = [r["wer"] for r in results if r["wer"] != "N/A"]
    valid_cers = [r["cer"] for r in results if r["cer"] != "N/A"]
    mean_wer = (sum(valid_wers) / len(valid_wers)) if valid_wers else 0.0
    mean_cer = (sum(valid_cers) / len(valid_cers)) if valid_cers else 0.0

    print("\n" + "="*60)
    print("                    INFERENCE SUMMARY                    ")
    print("="*60)
    print(f" Model Architecture   : Whisper '{args.model}' ({args.device.upper()})")
    print(f" Samples Processed    : {len(results)}")
    print(f" Total Audio Duration : {total_audio_sec:.2f} s ({total_audio_sec/60:.2f} min)")
    print(f" Total Wall Time      : {total_wall_sec:.2f} s")
    print(f" Overall Speed Factor : {avg_rtf:.2f}x Real-Time (Faster than real-time)")
    print(f" Average Latency      : {total_wall_sec / len(results):.3f} s / sample")
    if valid_wers:
        print(f" Mean Sample WER      : {mean_wer * 100:.2f}%")
        print(f" Mean Sample CER      : {mean_cer * 100:.2f}%")
    print(f" Peak Memory (RSS)    : {max(r['memory_rss_mb'] for r in results):.1f} MB")
    print("="*60)


if __name__ == "__main__":
    main()
