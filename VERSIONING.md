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
| `fix:` | `fix: behebe GPIO bug` | `0.1.0` → `0.1.1` (patch) |
| `feat:` | `feat: füge logging hinzu` | `0.1.0` → `0.2.0` (minor) |
| `BREAKING CHANGE` | `feat: neue API - BREAKING CHANGE` | `0.1.0` → `1.0.0` (major) |

### Manuelle Versionierung
```bash
python update_version.py patch   # 0.1.0 → 0.1.1
python update_version.py minor   # 0.1.0 → 0.2.0  
python update_version.py major   # 0.1.0 → 1.0.0
```

## 📝 Commit Message Format

Verwende [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Patch Version (Bugfixes)
git commit -m "fix: korrigiere debouncing logic"
git commit -m "docs: aktualisiere README"

# Minor Version (neue Features)
git commit -m "feat: füge error handling hinzu"
git commit -m "feat: implementiere logging system"

# Major Version (Breaking Changes)
git commit -m "feat: neue GPIO API - BREAKING CHANGE"
git commit -m "refactor: entferne alte API - BREAKING CHANGE"
```

## 🔧 Technische Details

### Dateien
- `update_version.py` - Haupt-Script für Versionierung
- `setup_versioning.py` - Installation und Setup
- `pre-commit-hook.sh` - Git Hook für Unix/Linux/Mac
- `pre-commit-hook.bat` - Git Hook für Windows

### Version Format
- Format: `MAJOR.MINOR.PATCH` (Semantic Versioning)
- Ort: Zeile 2 in `paketbox.py`
- Pattern: `# Version X.Y.Z`

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
```

## 🐛 Troubleshooting

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

## 📊 Beispiel-Workflow

```bash
# 1. Aktuelle Version: 0.2.1

# 2. Bugfix commit
git add .
git commit -m "fix: behebe GPIO timeout problem"
# → Version wird automatisch zu 0.2.2

# 3. Feature commit  
git add .
git commit -m "feat: füge watchdog timer hinzu"
# → Version wird automatisch zu 0.3.0

# 4. Breaking change
git add .
git commit -m "feat: neue API structure - BREAKING CHANGE"
# → Version wird automatisch zu 1.0.0
```

Das System ist vollständig automatisch und benötigt keine manuelle Intervention! 🎉
