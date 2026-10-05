"""
evaluate.py
Computes comprehensive speech recognition evaluation metrics from results.csv.
Calculates Word Error Rate (WER), Character Error Rate (CER), Match Error Rate (MER),
Word Information Lost (WIL), and Word Information Preserved (WIP) using JiWER.
Also profiles latency, throughput, and CPU/memory statistics.
"""

import os
import sys
import csv
import argparse
import statistics
import string
import re
from tabulate import tabulate
import jiwer


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_category_map():
    """Load sample metadata categories if transcripts.csv exists."""
    cat_map = {}
    csv_candidates = [
        os.path.join("transcripts", "transcripts.csv"),
        os.path.join("..", "transcripts", "transcripts.csv")
    ]
    for c in csv_candidates:
        if os.path.exists(c):
            with open(c, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fname = row.get("filename")
                    cat = row.get("category", "General")
                    if fname:
                        cat_map[fname] = cat
            break
    return cat_map


def main():
    parser = argparse.ArgumentParser(description="Evaluate Speech-to-Text Performance Metrics")
    parser.add_argument("results_csv", nargs="?", default="results.csv", help="Path to results CSV file")
    parser.add_argument("metrics_txt", nargs="?", default="output/metrics.txt", help="Path to save metrics summary")
    args = parser.parse_args()

    if not os.path.exists(args.results_csv):
        print(f"Error: Results file not found: {args.results_csv}")
        sys.exit(1)

    rows = []
    with open(args.results_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        print("Error: Results CSV is empty.")
        sys.exit(1)

    cat_map = load_category_map()

    refs = []
    hyps = []
    latencies = []
    cpu_times = []
    rtfs = []
    memories = []
    durations = []

    category_buckets = {}

    for r in rows:
        ref = r.get("reference", "")
        hyp = r.get("hypothesis", "")
        norm_ref = normalize_text(ref)
        norm_hyp = normalize_text(hyp)

        duration = float(r.get("duration_sec", 0.0))
        latency = float(r.get("latency_sec", 0.0))
        cpu_time = float(r.get("cpu_time_sec", 0.0))
        rtf = float(r.get("rtf_factor", 0.0))
        mem = float(r.get("memory_rss_mb", 0.0))

        durations.append(duration)
        latencies.append(latency)
        cpu_times.append(cpu_time)
        rtfs.append(rtf)
        memories.append(mem)

        refs.append(norm_ref)
        hyps.append(norm_hyp)

        # Categorization
        fname = r.get("audio_file", "")
        cat = cat_map.get(fname, "Uncategorized")
        if cat not in category_buckets:
            category_buckets[cat] = {"refs": [], "hyps": [], "latencies": [], "rtfs": []}
        category_buckets[cat]["refs"].append(norm_ref)
        category_buckets[cat]["hyps"].append(norm_hyp)
        category_buckets[cat]["latencies"].append(latency)
        category_buckets[cat]["rtfs"].append(rtf)

    # Compute Global ASR Metrics via JiWER
    global_wer = jiwer.wer(refs, hyps)
    global_cer = jiwer.cer(refs, hyps)
    global_mer = jiwer.mer(refs, hyps)
    global_wil = jiwer.wil(refs, hyps)
    global_wip = jiwer.wip(refs, hyps)

    # Latency & Hardware Stats
    total_audio = sum(durations)
    total_latency = sum(latencies)
    total_cpu = sum(cpu_times)
    mean_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    stdev_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    mean_rtf = statistics.mean(rtfs)
    overall_speed = total_audio / total_latency if total_latency > 0 else 0.0
    mean_mem = statistics.mean(memories)
    peak_mem = max(memories)

    # Category breakdown table
    cat_table = []
    for cat_name, data in sorted(category_buckets.items()):
        c_refs = data["refs"]
        c_hyps = data["hyps"]
        c_wer = jiwer.wer(c_refs, c_hyps) * 100
        c_cer = jiwer.cer(c_refs, c_hyps) * 100
        c_lat = statistics.mean(data["latencies"])
        c_rtf = statistics.mean(data["rtfs"])
        cat_table.append([cat_name, len(c_refs), f"{c_wer:.2f}%", f"{c_cer:.2f}%", f"{c_lat:.3f}s", f"{c_rtf:.2f}x"])

    headers_cat = ["Category", "Count", "WER", "CER", "Avg Latency", "Avg RTF"]
    table_str = tabulate(cat_table, headers=headers_cat, tablefmt="github")

    # Generate full report text
    report = []
    report.append("================================================================================")
    report.append("                 LOCAL SPEECH-TO-TEXT EVALUATION REPORT                         ")
    report.append("================================================================================")
    report.append(f" Total Samples Evaluated    : {len(rows)}")
    report.append(f" Total Audio Duration       : {total_audio:.2f} seconds ({total_audio/60:.2f} minutes)")
    report.append(f" Total Wall-Clock Latency   : {total_latency:.2f} seconds")
    report.append(f" Total CPU Processing Time  : {total_cpu:.2f} seconds")
    report.append(f" Overall Processing Speed   : {overall_speed:.2f}x Real-Time (audio duration / wall time)")
    report.append("")
    report.append("--- ACCURACY METRICS (JIWER) ---")
    report.append(f" Word Error Rate (WER)      : {global_wer * 100:.2f}%")
    report.append(f" Character Error Rate (CER) : {global_cer * 100:.2f}%")
    report.append(f" Match Error Rate (MER)     : {global_mer * 100:.2f}%")
    report.append(f" Word Info Lost (WIL)       : {global_wil * 100:.2f}%")
    report.append(f" Word Info Preserved (WIP)  : {global_wip * 100:.2f}%")
    report.append("")
    report.append("--- LATENCY & THROUGHPUT (CPU) ---")
    report.append(f" Mean Latency / Sample      : {mean_latency:.3f} s")
    report.append(f" Median Latency             : {median_latency:.3f} s")
    report.append(f" Latency Std Dev            : {stdev_latency:.3f} s")
    report.append(f" Min Latency                : {min(latencies):.3f} s")
    report.append(f" Max Latency                : {max(latencies):.3f} s")
    report.append(f" Mean Real-Time Factor (RTF): {mean_rtf:.2f}x")
    report.append("")
    report.append("--- RESOURCE UTILIZATION (CPU & RAM) ---")
    report.append(f" Mean Memory Usage (RSS)    : {mean_mem:.2f} MB")
    report.append(f" Peak Memory Usage (RSS)    : {peak_mem:.2f} MB")
    report.append("")
    report.append("--- CATEGORICAL PERFORMANCE BREAKDOWN ---")
    report.append(table_str)
    report.append("================================================================================")

    final_output = "\n".join(report)
    print(final_output)

    # Save to metrics file
    out_dir = os.path.dirname(args.metrics_txt)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.metrics_txt, "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"\nSaved metrics summary to: {os.path.abspath(args.metrics_txt)}")


if __name__ == "__main__":
    main()
