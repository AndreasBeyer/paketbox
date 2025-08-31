@echo off
REM Git Pre-Commit Hook für automatische Versionierung (Windows)
REM Installiere diesen Hook durch Kopieren nach .git\hooks\pre-commit.bat

echo 🔄 Automatische Versionierung wird durchgeführt...

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python nicht gefunden - Versionierung übersprungen
        exit /b 0
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

REM Führe Versionsaktualisierung aus
%PYTHON_CMD% update_version.py
if %errorlevel% equ 0 (
    echo ✅ Version erfolgreich aktualisiert
) else (
    echo ⚠️  Versionierung fehlgeschlagen - Commit wird trotzdem fortgesetzt
)

exit /b 0
