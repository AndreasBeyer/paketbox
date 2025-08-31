# Paketbox Steuerung 📦

Dieses Projekt steuert eine intelligente Paketbox mit einem Raspberry Pi. Die Box kann Pakete sicher aufnehmen, automatisch verriegeln und entleeren. Die Steuerung erfolgt über Motoren, Sensoren und Relais mit professioneller Fehlerbehandlung und Logging.

## ✨ Features
- **Automatisches Öffnen und Schließen** der Entleerungsklappen
- **Intelligente Türverriegelung** nach Paketeingang
- **Umfassende Sensorüberwachung** für alle Klappen und Türen
- **Robuste Fehlerbehandlung** mit automatischen ERROR-States
- **Professionelles Logging** mit Datei- und Console-Output
- **Mock-Modus** für lokale Entwicklung ohne Hardware
- **Konfigurierbare Parameter** über zentrale Config-Klasse
- **Thread-sichere Zustandsverwaltung** mit Locking-Mechanismen
- **Automatische Versionierung** basierend auf Commit-Types

## 🔧 Hardware
- **Raspberry Pi** mit GPIO-Steuerung
- **2 Motoren** für Entleerungsklappen mit Endlagensensoren
- **Relais-Board** für Motorsteuerung und Türverriegelung
- **Sensoren**:
  - Endlagensensoren für beide Klappen (offen/geschlossen)
  - Türsensoren für Paketzustellertür
  - Briefkastensensoren für Entnahme
  - Bewegungsmelder für Einklemmschutz
- **Taster** für Gartentüröffner (Nr. 6 und 8)

## 🚀 Quick Start

### Installation
1. **Python 3** installieren (3.7+)
2. **Repository klonen**:
   ```bash
   git clone https://github.com/AndreasBeyer/max_paket_box.git
   cd max_paket_box
   ```
3. **Automatische Versionierung einrichten**:
   ```bash
   python setup_versioning.py
   ```
4. **Abhängigkeiten** (nur auf Raspberry Pi):
   ```bash
   pip install RPi.GPIO
   ```

### Erste Schritte
```bash
# Lokaler Test (Mock-Modus)
python paketbox.py

# Tests ausführen
python -m pytest tests/ -v
# oder
python tests/run_tests.py

# Version manuell erhöhen
python update_version.py patch
```

### Produktive Verwendung
```bash
# Auf Raspberry Pi
sudo python paketbox.py
```

## 🛠️ Entwicklung & Test

### Lokale Entwicklung
```bash
# Mock-Modus für Entwicklung ohne Hardware
python paketbox.py
# Ausgabe: "MockGPIO initialisiert - Hardware-Simulation aktiv"

# Tests ausführen (28 Tests, Dauer: ~65 Sekunden)
python tests/run_tests.py

# Spezifische Tests
python -m unittest tests.test_paketbox.TestPaketBox.test_Klappen_oeffnen_success -v
```

### Logging & Debugging
```bash
# Log-Datei überwachen
tail -f paketbox.log

# Debug-Level erhöhen (in paketbox.py)
logging.basicConfig(level=logging.DEBUG)
```

### Code-Qualität
- **GPIO-Debouncing**: Verhindert Mehrfachauslösung von Sensoren
- **Thread-Safe**: Alle Zustandsänderungen sind thread-sicher implementiert
- **Error Recovery**: Automatische ERROR-States bei Hardware-Fehlern
- **Konfiguration**: Zentrale Config-Klasse für alle Parameter

### Deployment
```bash
# Lokal testen
python paketbox.py

# Auf Raspberry Pi übertragen
./deploy_paketbox.sh     # Linux/macOS
deploy_paketbox.bat      # Windows
```

## 📁 Projektstruktur

```
max_paket_box/
├── paketbox.py           # Hauptsteuerung (Version 0.3.0)
├── tests/
│   ├── test_paketbox.py  # Umfassende Unit Tests
│   └── run_tests.py      # Test Runner mit detailliertem Output
├── versioning/
│   ├── update_version.py  # Automatische Versionsverwaltung
│   ├── setup_versioning.py # Installation der Git Hooks
│   └── VERSIONING.md      # Versionierung Dokumentation
├── hooks/
│   ├── pre-commit        # Git Hook (Unix)
│   └── pre-commit.bat    # Git Hook (Windows)
├── paketbox.log          # Strukturierte Log-Datei
├── README.md             # Diese Datei
└── deploy_paketbox.*     # Deployment Scripts
```

### Neue Komponenten (Version 0.3.0)
- **Automatische Versionierung**: Semantische Versionsnummern basierend auf Conventional Commits
- **Strukturiertes Logging**: Datei- und Konsolen-Logging mit verschiedenen Log-Leveln
- **Robuste Fehlerbehandlung**: Automatische ERROR-Zustände bei Hardware-Problemen
- **Thread-sichere Implementierung**: Zuverlässige Zustandsverwaltung ohne Race Conditions
- **Plattformübergreifende Entwicklung**: MockGPIO für Hardware-unabhängige Entwicklung

## 🔄 Automatische Versionierung

Das Projekt verwendet automatische Versionierung basierend auf [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: neue Funktion     → MINOR Version (0.3.0 → 0.4.0)
fix: Bugfix            → PATCH Version (0.3.0 → 0.3.1)  
BREAKING CHANGE:       → MAJOR Version (0.3.0 → 1.0.0)
```

**Setup**: `python setup_versioning.py`
**Dokumentation**: Siehe `versioning/VERSIONING.md`

## Lizenz
MIT

## Autor
Andreas Beyer
