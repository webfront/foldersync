@echo off
REM Navigate to the directory where this script is located
cd /d "%~dp0"

REM Run the backup script
python src/main.py --run-backup

REM Optional: Check exit code (Task Scheduler handles this, but useful for manual runs)
if %ERRORLEVEL% NEQ 0 (
    echo Backup failed with error level %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
