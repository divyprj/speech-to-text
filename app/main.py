"""
app/main.py
Main entrypoint for Local Speech-to-Text Application.
Starts FastAPI local server on 127.0.0.1:8765 and opens the browser.
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.routes import router as api_router

STATIC_DIR = ROOT_DIR / "static"

app = FastAPI(
    title="Local Transcriber",
    description="Offline Speech-to-Text application running on consumer CPU hardware",
    version="1.0.0"
)

# Allow local CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Local Transcriber"}

# Serve static frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "message": "Local Transcriber API is running"}


def open_browser(port: int):
    """Wait for server to start and automatically open the application in browser."""
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"\n[Local Transcriber] Opening interface in browser: {url}\n", flush=True)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    if sys.platform == "win32":
        try:
            os.system(f'start "" "{url}"')
        except Exception:
            pass


def main():
    # If PORT is specified (cloud/Docker/Render), use it. Local default is 8765.
    is_cloud = bool(os.environ.get("PORT") or os.environ.get("RENDER"))
    host = os.environ.get("HOST", "0.0.0.0" if is_cloud else "127.0.0.1")
    port = int(os.environ.get("PORT", "8765"))

    print("="*65)
    print("              LOCAL TRANSCRIBER - OFFLINE SPEECH-TO-TEXT        ")
    print("="*65)
    print(f" Engine URL        : http://{host}:{port}")
    print(f" Privacy           : 100% Offline (No cloud, zero external calls)")
    print(f" Static Assets     : {STATIC_DIR}")
    print("="*65 + "\n")

    # Launch browser only on local desktop
    if not is_cloud:
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Start server
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
