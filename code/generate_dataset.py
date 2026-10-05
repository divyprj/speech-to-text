"""
generate_dataset.py
Generates 50 diverse audio clips (16kHz 16-bit mono WAV) and corresponding reference transcripts
covering diverse domains: phonetically balanced sentences, numbers/dates, technical jargon,
conversational queries, varied speech rates, and additive noise to test ASR robustness.
"""

import os
import sys
import subprocess
import tempfile
import numpy as np
import soundfile as sf
import csv

AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio_samples"))
TRANSCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "transcripts"))

DATASET_SPECS = [
    # 1-10: Phonetically balanced Harvard sentences (clean speech, varied speakers)
    {
        "id": "sample_001",
        "text": "The birch canoe slid on the smooth planks.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_002",
        "text": "Glue the sheet to the dark blue background.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_003",
        "text": "Four hours of steady work faced us.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_004",
        "text": "A large size in stockings is hard to sell.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_005",
        "text": "The boy was there when the sun rose.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_006",
        "text": "A rod is used to catch pink salmon.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_007",
        "text": "The source of the huge river is the clear spring.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_008",
        "text": "Kick the ball straight into the goal.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_009",
        "text": "The jacket hangs on the wooden hook near the door.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },
    {
        "id": "sample_010",
        "text": "Two blue fish swam through the cold water.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Harvard Sentence"
    },

    # 11-20: Conversational, commands, and customer inquiries
    {
        "id": "sample_011",
        "text": "Could you please explain how to reset my account password?",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_012",
        "text": "What is the expected delivery date for order number nine four two?",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_013",
        "text": "Please turn off the living room lights and set the thermostat to seventy degrees.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_014",
        "text": "Can you check if there are any available flights to Chicago tomorrow morning?",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_015",
        "text": "I would like to schedule an appointment with the doctor next Tuesday at two o'clock.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_016",
        "text": "Hello, thank you for calling customer service. How may I direct your call today?",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_017",
        "text": "Show me the top five trending songs on the international billboard chart.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_018",
        "text": "Remind me to submit the quarterly financial spreadsheet before Friday evening.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_019",
        "text": "Where is the nearest electric vehicle charging station in this neighborhood?",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },
    {
        "id": "sample_020",
        "text": "Can you summarize the main conclusions of this research paper in three bullet points?",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Conversational"
    },

    # 21-30: Numerical data, dates, phone numbers, and financial figures
    {
        "id": "sample_021",
        "text": "The company revenue increased by fifteen percent to four million eight hundred thousand dollars.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_022",
        "text": "Her flight arrives on October twenty fourth at gate number forty seven.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_023",
        "text": "The transaction identification code is seven eight nine dash five four three.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_024",
        "text": "Please confirm the balance transfer of twelve hundred dollars from account five zero one.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_025",
        "text": "Inflation fell from seven point eight percent to three point two percent over twelve months.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_026",
        "text": "The customer phone number is five five five zero one nine eight.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_027",
        "text": "Total assets under management reached twelve point five billion dollars in the third quarter.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_028",
        "text": "The meeting is confirmed for November sixteenth from nine thirty to eleven o'clock.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_029",
        "text": "Our office is located at suite seven hundred on eighty fifth avenue.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },
    {
        "id": "sample_030",
        "text": "The stock index dropped twenty eight points closing at four thousand three hundred.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Numeric & Financial"
    },

    # 31-40: Technical, scientific, and computing vocabulary
    {
        "id": "sample_031",
        "text": "Artificial intelligence models require extensive training on diverse datasets.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_032",
        "text": "Quantization reduces memory footprint and accelerates CPU inference significantly.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_033",
        "text": "The microservices architecture communicates through secure lightweight APIs.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_034",
        "text": "Word error rate measures the proportion of substitutions deletions and insertions.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_035",
        "text": "The transformer encoder processes acoustic features through self-attention layers.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_036",
        "text": "Linear algebra operations are optimized with vector instructions and multi-threading.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_037",
        "text": "The database query executed within twelve milliseconds utilizing indexed columns.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_038",
        "text": "Continuous integration pipelines run unit tests and static code analysis automatically.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_039",
        "text": "Spectrogram features are converted to mel frequency filter banks for acoustic analysis.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },
    {
        "id": "sample_040",
        "text": "Asynchronous network sockets enable high throughput and concurrent connection handling.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.0, "category": "Technical"
    },

    # 41-45: Varied speech rates (Fast: rate +2, Slow: rate -2)
    {
        "id": "sample_041",
        "text": "Please hurry up and download the latest software update before the server reboots.",
        "voice": "Microsoft David Desktop", "rate": 2, "noise": 0.0, "category": "Fast Speech"
    },
    {
        "id": "sample_042",
        "text": "Quickly verify that all security protocols are strictly followed throughout the system.",
        "voice": "Microsoft Zira Desktop", "rate": 3, "noise": 0.0, "category": "Fast Speech"
    },
    {
        "id": "sample_043",
        "text": "Take your time and carefully read every instruction printed in this detailed manual.",
        "voice": "Microsoft David Desktop", "rate": -2, "noise": 0.0, "category": "Slow Speech"
    },
    {
        "id": "sample_044",
        "text": "Speak clearly and pronounce each syllable deliberately to ensure accurate transcription.",
        "voice": "Microsoft Zira Desktop", "rate": -2, "noise": 0.0, "category": "Slow Speech"
    },
    {
        "id": "sample_045",
        "text": "The rapid development of open source software has transformed modern technology.",
        "voice": "Microsoft David Desktop", "rate": 2, "noise": 0.0, "category": "Fast Speech"
    },

    # 46-50: Noisy Speech (Simulated acoustic noise, room reverb, low SNR)
    {
        "id": "sample_046",
        "text": "The captain ordered the crew to lower the sails as the storm approached.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.015, "category": "Noisy (Mild)"
    },
    {
        "id": "sample_047",
        "text": "Modern automated speech recognition systems remain remarkably robust in noisy environments.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.025, "category": "Noisy (Moderate)"
    },
    {
        "id": "sample_048",
        "text": "Heavy rain and distant thunder created continuous background noise during the recording.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.035, "category": "Noisy (Heavy)"
    },
    {
        "id": "sample_049",
        "text": "Coffee shops and open office spaces present significant acoustic challenges for microphones.",
        "voice": "Microsoft Zira Desktop", "rate": 0, "noise": 0.020, "category": "Noisy (Moderate)"
    },
    {
        "id": "sample_050",
        "text": "Evaluation metrics like word error rate determine how effectively filters eliminate interference.",
        "voice": "Microsoft David Desktop", "rate": 0, "noise": 0.040, "category": "Noisy (Heavy)"
    }
]


def synthesize_audio(text, voice, rate, temp_wav):
    """Synthesize speech using Windows SAPI through PowerShell."""
    ps_cmd = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('{voice}')
$synth.Rate = {rate}
$synth.SetOutputToWaveFile('{temp_wav}')
$synth.Speak('{text.replace("'", "''")}')
$synth.Dispose()
"""
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"PowerShell TTS failed: {result.stderr}")


def process_audio(raw_wav, final_wav, noise_level):
    """
    Standardize audio to 16kHz, 16-bit mono PCM.
    If noise_level > 0, inject realistic acoustic background noise.
    """
    data, sr = sf.read(raw_wav)
    if len(data.shape) > 1:
        data = data.mean(axis=1)

    # Resample to 16kHz if needed
    target_sr = 16000
    if sr != target_sr:
        num_samples = int(len(data) * target_sr / sr)
        orig_indices = np.linspace(0, len(data) - 1, len(data))
        target_indices = np.linspace(0, len(data) - 1, num_samples)
        data = np.interp(target_indices, orig_indices, data)
        sr = target_sr

    # Normalize audio amplitude
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data = data / max_val * 0.9

    # Add noise if requested
    if noise_level > 0:
        np.random.seed(42)
        # Combine pink noise (colored) + gaussian white noise for realism
        white_noise = np.random.normal(0, 1, len(data))
        # Simple IIR filter for pink-ish noise
        pink_noise = np.convolve(white_noise, np.ones(5)/5, mode='same')
        noise = (0.7 * pink_noise + 0.3 * white_noise)
        noise = noise / np.max(np.abs(noise)) * noise_level
        data = data + noise
        # Re-normalize to prevent clipping
        max_peak = np.max(np.abs(data))
        if max_peak > 1.0:
            data = data / max_peak * 0.95

    sf.write(final_wav, data, 16000, subtype='PCM_16')
    duration = len(data) / 16000.0
    return duration


def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

    print(f"Generating 50 speech samples in {AUDIO_DIR}...")
    metadata = []

    for item in DATASET_SPECS:
        sample_id = item["id"]
        wav_name = f"{sample_id}.wav"
        txt_name = f"{sample_id}.txt"
        wav_path = os.path.join(AUDIO_DIR, wav_name)
        txt_path = os.path.join(TRANSCRIPTS_DIR, txt_name)

        # Write reference transcript file
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(item["text"])

        # Synthesize via SAPI
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            synthesize_audio(item["text"], item["voice"], item["rate"], tmp_path)
            duration = process_audio(tmp_path, wav_path, item["noise"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        metadata.append({
            "filename": wav_name,
            "transcript_file": txt_name,
            "reference_transcript": item["text"],
            "duration_sec": round(duration, 2),
            "speaker_voice": item["voice"],
            "speech_rate": item["rate"],
            "noise_level": item["noise"],
            "category": item["category"]
        })
        print(f"  [{sample_id}] Generated ({duration:.2f}s) - Category: {item['category']}")

    # Save transcripts CSV
    csv_path = os.path.join(TRANSCRIPTS_DIR, "transcripts.csv")
    fieldnames = ["filename", "transcript_file", "reference_transcript", "duration_sec", "speaker_voice", "speech_rate", "noise_level", "category"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata)

    total_duration = sum(item["duration_sec"] for item in metadata)
    print(f"\nDataset generation complete! 50 files saved.")
    print(f"Transcripts CSV saved to: {csv_path}")
    print(f"Total audio duration: {total_duration:.1f} seconds (~{total_duration/60:.2f} minutes).")


if __name__ == "__main__":
    main()
