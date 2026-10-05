@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Local Transcriber • Offline Speech-to-Text

echo ===============================================================================
echo                LOCAL TRANSCRIBER • OFFLINE SPEECH-TO-TEXT
echo ===============================================================================
echo.

:: 1. Locate Virtual Environment / Python
set "PYTHON_EXE="
if exist "%~dp0stt-env\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0stt-env\Scripts\python.exe"
    echo [*] Using local environment: %~dp0stt-env
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python was not found on your system PATH or in stt-env.
        echo Please install Python 3.8+ or check README.md.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=python"
    echo [*] Using system Python.
)

:: 2. Handle CLI flags if passed
if "%~1"=="--cli" goto :cli_menu
if "%~1"=="-h" goto :cli_help
if "%~1"=="--help" goto :cli_help
if not "%~1"=="" (
    echo [*] Running in CLI mode with provided arguments...
    "%PYTHON_EXE%" "%~dp0code\transcribe.py" %*
    goto :end
)

:: 3. Default Action: Launch Interactive Web UI Immediately
:launch_ui
echo.
echo ===============================================================================
echo [1/2] Starting Local Transcriber Web Interface...
echo [2/2] Opening browser at http://127.0.0.1:8765 ...
echo ===============================================================================
echo (Keep this window open while using the app. Press Ctrl+C anytime to stop.)
echo.

:: Launch browser directly from Windows batch
start "" "http://127.0.0.1:8765"

:: Start FastAPI Server
"%PYTHON_EXE%" "%~dp0app\main.py"
goto :end

:cli_menu
echo.
echo Choose a CLI action:
echo  [1] Run Full CLI Benchmark (Transcribe 50 samples + Evaluate Whisper Small)
echo  [2] Run Quick CLI Benchmark (Whisper Base)
echo  [3] Recompute Evaluation Metrics from results.csv
echo  [4] Re-generate 50 Benchmark Audio Samples and Transcripts
echo  [5] Exit
echo.
set /p "CHOICE=Enter choice [1-5]: "
if "%CHOICE%"=="1" (
    "%PYTHON_EXE%" "%~dp0code\transcribe.py" "%~dp0audio_samples" "%~dp0transcripts" "%~dp0results.csv" --model small
    "%PYTHON_EXE%" "%~dp0code\evaluate.py" "%~dp0results.csv" "%~dp0output\metrics.txt"
    goto :end
)
if "%CHOICE%"=="2" (
    "%PYTHON_EXE%" "%~dp0code\transcribe.py" "%~dp0audio_samples" "%~dp0transcripts" "%~dp0results.csv" --model base
    "%PYTHON_EXE%" "%~dp0code\evaluate.py" "%~dp0results.csv" "%~dp0output\metrics.txt"
    goto :end
)
if "%CHOICE%"=="3" (
    "%PYTHON_EXE%" "%~dp0code\evaluate.py" "%~dp0results.csv" "%~dp0output\metrics.txt"
    goto :end
)
if "%CHOICE%"=="4" (
    "%PYTHON_EXE%" "%~dp0code\generate_dataset.py"
    goto :end
)
goto :end

:cli_help
"%PYTHON_EXE%" "%~dp0code\transcribe.py" --help
goto :end

:end
echo.
echo ===============================================================================
echo Finished.
echo ===============================================================================
pause
