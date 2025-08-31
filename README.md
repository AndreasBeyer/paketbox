# Paketbox Steuerung

Dieses Projekt steuert eine Paketbox mit einem Raspberry Pi. Die Box kann Pakete sicher aufnehmen und automatisch verriegeln und entleeren. Die Steuerung erfolgt über Motoren, Sensoren und Relais.

## Features
- Automatisches Öffnen und Schließen der Klappen
- Verriegelung der Paket-Tür nach dem Schließen
- Sensorüberwachung für Klappen und Türen
- Fehlererkennung und -behandlung
- Mock-Modus für lokale Tests ohne Hardware
- Konfigurierbare Zeitsteuerung für Motoren und Klappen

## Hardware
- Raspberry Pi (GPIO-Steuerung)
- 2 Motoren für Klappen
- Relais für Motoren und Türverriegelung
- Sensoren für Endlagen und Türstatus

## Installation
1. Python 3 installieren
2. Abhängigkeiten installieren (nur auf Raspberry Pi):
   ```bash
   pip install RPi.GPIO
   ```
3. Projekt klonen:
   ```bash
   git clone <repo-url>
   ```
4. Script ausführen:
   ```bash
   python paketbox.py
   ```

## Entwicklung & Test
- Im Mock-Modus kann das Script auch ohne Raspberry Pi getestet werden.
- Die Steuerung und Logik sind in `paketbox.py` implementiert.
- Einstellungen und Hardware-Pins sind im Code dokumentiert.

## Projektstruktur
```
├── paketbox.py         # Hauptskript
├── test_paketbox.py    # Tests (optional)
├── deploy_paketbox.sh  # Deployment-Skript (Linux)
├── deploy_paketbox.bat # Deployment-Skript (Windows)
├── .gitignore          # Git Ignore
└── README.md           # Projektbeschreibung
```

## Lizenz
MIT

## Autor
Andreas Beyer
