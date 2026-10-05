import time
import os
from playwright.sync_api import sync_playwright

def main():
    os.makedirs("screenshots", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("Navigating to Files tab...")
        page.goto("http://127.0.0.1:8765", wait_until="networkidle")
        page.click('[data-tab="tab-files"]')
        time.sleep(0.5)

        # Upload audio_samples/sample_001.wav
        audio_file = os.path.abspath("audio_samples/sample_001.wav")
        print(f"Uploading {audio_file}...")
        page.set_input_files("#fileInput", audio_file)
        time.sleep(0.5)

        # Click Transcribe
        print("Clicking Transcribe...")
        page.click("#startFileTranscribeBtn")

        # Wait for transcription completion (poll until #fileResultBox is visible)
        print("Waiting for transcription to complete...")
        page.wait_for_selector("#fileResultBox", state="visible", timeout=60000)
        time.sleep(1)

        print("Capturing transcript synced view...")
        page.screenshot(path="screenshots/06_transcription_synced.png", full_page=True)

        # Test search
        print("Testing transcript search...")
        page.fill("#fileSearchInput", "canoe")
        time.sleep(0.5)
        page.screenshot(path="screenshots/07_transcript_search.png", full_page=True)

        browser.close()
        print("Interactive sync test passed and screenshots saved!")

if __name__ == "__main__":
    main()
