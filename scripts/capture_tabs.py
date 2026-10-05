import time
from playwright.sync_api import sync_playwright

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://127.0.0.1:8765", timeout=30000)
        time.sleep(2)

        # Tab 1: Dictate
        page.click("div[data-tab='tab-dictation']")
        time.sleep(1)
        page.screenshot(path="screenshots/01_dictate_tab.png", full_page=True)
        page.screenshot(path=r"C:\Dev\gemini-gpt-bridge\bridge\screenshots\01_dictate_tab.png", full_page=True)
        print("Captured 01_dictate_tab.png")

        # Tab 2: Files
        page.click("div[data-tab='tab-files']")
        time.sleep(1)
        page.screenshot(path="screenshots/02_files_tab.png", full_page=True)
        page.screenshot(path=r"C:\Dev\gemini-gpt-bridge\bridge\screenshots\02_files_tab.png", full_page=True)
        print("Captured 02_files_tab.png")

        # Tab 3: Quality
        page.click("div[data-tab='tab-quality']")
        time.sleep(1)
        page.screenshot(path="screenshots/03_quality_tab.png", full_page=True)
        page.screenshot(path=r"C:\Dev\gemini-gpt-bridge\bridge\screenshots\03_quality_tab.png", full_page=True)
        print("Captured 03_quality_tab.png")

        # Tab 4: Settings
        page.click("div[data-tab='tab-settings']")
        time.sleep(1)
        page.screenshot(path="screenshots/04_settings_tab.png", full_page=True)
        page.screenshot(path=r"C:\Dev\gemini-gpt-bridge\bridge\screenshots\04_settings_tab.png", full_page=True)
        print("Captured 04_settings_tab.png")

        browser.close()

if __name__ == "__main__":
    capture()
