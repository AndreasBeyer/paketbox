#!/bin/sh
#
# Git Pre-Commit Hook für automatische Versionierung
# Installiere diesen Hook mit: chmod +x .git/hooks/pre-commit
#
# Dieser Hook:
# 1. Erkennt den Commit-Typ aus der Commit-Message
# 2. Erhöht die Versionsnummer entsprechend
# 3. Fügt die geänderte Datei zum Commit hinzu

echo "🔄 Automatische Versionierung wird durchgeführt..."

# Prüfe ob Python verfügbar ist
if ! command -v python3 >/dev/null 2>&1; then
    if ! command -v python >/dev/null 2>&1; then
        echo "❌ Python nicht gefunden - Versionierung übersprungen"
        exit 0
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Führe Versionsaktualisierung aus
if $PYTHON_CMD update_version.py; then
    echo "✅ Version erfolgreich aktualisiert"
else
    echo "⚠️  Versionierung fehlgeschlagen - Commit wird trotzdem fortgesetzt"
fi

exit 0
