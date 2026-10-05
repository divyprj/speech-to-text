import time
import os
from playwright.sync_api import sync_playwright

def main():
    os.makedirs("screenshots", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Capture console errors if any
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("Navigating to http://127.0.0.1:8765...")
        page.goto("http://127.0.0.1:8765", wait_until="networkidle")
        time.sleep(1)

        # 1. Dictate Tab
        print("Capturing Dictate tab...")
        page.screenshot(path="screenshots/01_dictate_tab.png", full_page=True)

        # 2. Files Tab
        print("Capturing Files tab...")
        page.click('[data-tab="tab-files"]')
        time.sleep(0.5)
        page.screenshot(path="screenshots/02_files_tab.png", full_page=True)

        # 3. Quality Tab
        print("Capturing Quality tab...")
        page.click('[data-tab="tab-quality"]')
        time.sleep(0.8)
        page.screenshot(path="screenshots/03_quality_tab.png", full_page=True)

        # 4. Settings Tab
        print("Capturing Settings tab...")
        page.click('[data-tab="tab-settings"]')
        time.sleep(0.5)
        page.screenshot(path="screenshots/04_settings_tab.png", full_page=True)

        # 5. Open Drawer from Quality tab
        print("Opening Drawer...")
        page.click('[data-tab="tab-quality"]')
        time.sleep(0.5)
        # click first 'View' button in table
        view_btn = page.query_selector('#benchmarkTbody button.btn-outline')
        if view_btn:
            view_btn.click()
            time.sleep(0.5)
            page.screenshot(path="screenshots/05_drawer_view.png", full_page=True)

        browser.close()
        print(f"Screenshots saved. Console errors detected: {len(errors)}")
        if errors:
            print("Errors:", errors)

if __name__ == "__main__":
    main()
