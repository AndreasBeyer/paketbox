# Automatische Versionierung 🤖

Dieses System erhöht automatisch die Versionsnummer in `paketbox.py` basierend auf Commit-Types.

## 🚀 Installation

```bash
python setup_versioning.py
```

Das Setup-Script:
- ✅ Installiert Git Hooks automatisch
- ✅ Testet das Versionierungs-System
- ✅ Zeigt Verwendungshinweise

## 📋 Wie es funktioniert

### Automatische Versionierung (empfohlen)
Bei jedem `git commit` wird automatisch die Version erhöht:

| Commit Type | Beispiel | Version Change |
|-------------|----------|----------------|
| `fix:` | `fix: behebe GPIO bug` | `0.7.0` → `0.7.1` (patch) |
| `feat:` | `feat: füge MQTT hinzu` | `0.7.0` → `0.8.0` (minor) |
| `BREAKING CHANGE` | `feat: neue API - BREAKING CHANGE` | `0.7.0` → `1.0.0` (major) |

### Manuelle Versionierung
```bash
python update_version.py patch   # 0.7.0 → 0.7.1
python update_version.py minor   # 0.7.0 → 0.8.0  
python update_version.py major   # 0.7.0 → 1.0.0
```

## 📝 Commit Message Format

Verwende [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Patch Version (Bugfixes)
git commit -m "fix: korrigiere debouncing logic"
git commit -m "docs: aktualisiere README"
git commit -m "fix: behebe Timer-Leckage in TimerManager"

# Minor Version (neue Features)
git commit -m "feat: füge MQTT integration hinzu"
git commit -m "feat: implementiere modulare Architektur"
git commit -m "feat: füge TimerManager für sichere Timer-Verwaltung hinzu"

# Major Version (Breaking Changes)
git commit -m "feat: neue GPIO API - BREAKING CHANGE"
git commit -m "refactor: entferne alte Monolith-Struktur - BREAKING CHANGE"
```

## 🔧 Technische Details

### Dateien im Projekt-Root
- `update_version.py` - Haupt-Script für Versionierung
- `setup_versioning.py` - Installation und Setup
- `pre-commit-hook.sh` - Git Hook für Unix/Linux/Mac
- `pre-commit-hook.bat` - Git Hook für Windows

### Version Format
- **Format**: `MAJOR.MINOR.PATCH` (Semantic Versioning)
- **Ort**: Zeile 2 in `paketbox.py`
- **Pattern**: `# Version X.Y.Z`
- **Aktuelle Version**: 0.7.0 (Modulare Architektur)

### Git Hook Installation
Das Setup-Script kopiert automatisch den richtigen Hook:
- **Windows**: `.git/hooks/pre-commit.bat`
- **Unix/Linux/Mac**: `.git/hooks/pre-commit` (mit Execute-Berechtigung)

## 🧪 Testing

```bash
# Teste das Versionierungs-Script
python update_version.py

# Teste mit spezifischem Increment
python update_version.py minor

# Validiere aktuelle Version
grep "# Version" paketbox.py
```

## � Versions-Historie

### Version 0.7.0 (Aktuelle Version)
- **Modulare Architektur**: Aufspaltung in separate Module
- **TimerManager**: Sichere Timer-Verwaltung
- **MQTT Integration**: IoT-Benachrichtigungen mit Fallback
- **Verbesserte Fehlerbehandlung**: Umfassende Error-Recovery
- **Erweiterte Tests**: Motor-Blockage und Timer-Tests

### Historische Versionen
- **0.6.x**: Erweiterte GPIO-Funktionalität
- **0.5.x**: Thread-sichere Zustandsverwaltung
- **0.4.x**: Automatische Versionierung eingeführt
- **0.3.x**: Grundlegende Paketbox-Funktionalität
- **0.2.x**: GPIO-Steuerung und Motoren
- **0.1.x**: Initiale Implementierung

## �🐛 Troubleshooting

### "Python nicht gefunden"
Stelle sicher, dass Python in der PATH-Variable ist:
```bash
python --version
# oder
python3 --version
```

### "Git Hook wird nicht ausgeführt"
1. Prüfe Hook-Berechtigung (Unix): `ls -la .git/hooks/pre-commit`
2. Führe Setup erneut aus: `python setup_versioning.py`
3. Teste manuell: `python update_version.py`

### "Version nicht gefunden"
Stelle sicher, dass `paketbox.py` die Zeile enthält:
```python
# Version X.Y.Z
```

### Hook-Debugging
```bash
# Windows
.git\hooks\pre-commit.bat

# Unix/Linux/Mac
.git/hooks/pre-commit
```

## 📊 Beispiel-Workflows

### Typischer Development-Workflow
```bash
# 1. Aktuelle Version: 0.7.0

# 2. Bugfix in TimerManager
git add .
git commit -m "fix: behebe Timer-Leckage bei Nothalt"
# → Version wird automatisch zu 0.7.1

# 3. Neue MQTT-Funktionalität
git add .
git commit -m "feat: füge MQTT-Retry-Logik hinzu"
# → Version wird automatisch zu 0.8.0

# 4. Breaking change in der API
git add .
git commit -m "feat: neue Handler-API - BREAKING CHANGE: ResetErrorState Parameter geändert"
# → Version wird automatisch zu 1.0.0
```

### Release-Management
```bash
# Vor einem Release
python update_version.py minor  # Manueller Bump für Release-Kandidat
python tests/run_tests.py       # Alle Tests müssen bestehen
python paketbox.py              # Funktionstest
git tag v$(grep "# Version" paketbox.py | cut -d' ' -f3)
```

## 🎯 Best Practices

### Commit Messages
- **fix**: Für Bugfixes, die rückwärtskompatibel sind
- **feat**: Für neue Features, die rückwärtskompatibel sind
- **BREAKING CHANGE**: Für Changes, die rückwärts-inkompatibel sind
- **docs**: Für Dokumentation (keine Version-Änderung)
- **test**: Für Tests (keine Version-Änderung)

### Versionierungs-Strategie
- **PATCH**: Bugfixes, kleine Verbesserungen
- **MINOR**: Neue Features, rückwärtskompatibel
- **MAJOR**: Breaking Changes, API-Änderungen

Das System ist vollständig automatisch und benötigt keine manuelle Intervention! 🎉

**Aktuelle Version**: 0.7.0 - Modulare Architektur mit verbesserter Fehlerbehandlung
