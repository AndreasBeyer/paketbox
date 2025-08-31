#!/usr/bin/env python3
"""
Setup Script für automatische Versionierung
===========================================

Installiert Git Hooks für automatische Versionsnummer-Updates.
"""

import os
import shutil
import stat
import sys
from pathlib import Path

def setup_git_hooks():
    """Setup Git hooks for automatic versioning."""
    project_root = Path(__file__).parent
    git_hooks_dir = project_root / ".git" / "hooks"
    
    if not git_hooks_dir.exists():
        print("❌ .git/hooks Verzeichnis nicht gefunden. Stelle sicher, dass du in einem Git-Repository bist.")
        return False
    
    # Determine the appropriate hook based on OS
    if os.name == 'nt':  # Windows
        hook_source = project_root / "pre-commit-hook.bat"
        hook_target = git_hooks_dir / "pre-commit.bat"
    else:  # Unix/Linux/Mac
        hook_source = project_root / "pre-commit-hook.sh"
        hook_target = git_hooks_dir / "pre-commit"
    
    try:
        # Copy hook file
        shutil.copy2(hook_source, hook_target)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            current_permissions = stat.S_IMODE(os.lstat(hook_target).st_mode)
            os.chmod(hook_target, current_permissions | stat.S_IEXEC)
        
        print(f"✅ Git Hook erfolgreich installiert: {hook_target}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Installieren des Git Hooks: {e}")
        return False

def test_versioning():
    """Test the versioning script."""
    project_root = Path(__file__).parent
    version_script = project_root / "update_version.py"
    
    print("\n🧪 Teste Versionierungs-Script...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(version_script)], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Versionierungs-Script funktioniert korrekt")
            print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Versionierungs-Script Fehler: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

def show_usage_info():
    """Show usage information."""
    print("\n📖 Verwendung der automatischen Versionierung:")
    print("=" * 50)
    print("1. 🤖 Automatisch (empfohlen):")
    print("   - Versionierung erfolgt automatisch bei jedem Commit")
    print("   - feat: commits → minor version bump (0.1.0 → 0.2.0)")
    print("   - fix: commits → patch version bump (0.1.0 → 0.1.1)")
    print("   - BREAKING CHANGE → major version bump (0.1.0 → 1.0.0)")
    print()
    print("2. 🖐️ Manuell:")
    print("   python update_version.py patch   # 0.1.0 → 0.1.1")
    print("   python update_version.py minor   # 0.1.0 → 0.2.0")
    print("   python update_version.py major   # 0.1.0 → 1.0.0")
    print()
    print("3. 📝 Commit Message Beispiele:")
    print("   git commit -m 'fix: behebe GPIO debouncing'")
    print("   git commit -m 'feat: füge logging hinzu'")
    print("   git commit -m 'feat: neue API - BREAKING CHANGE'")

def main():
    """Main setup function."""
    print("🚀 Setup für automatische Versionierung")
    print("=" * 40)
    
    success = True
    
    # Setup Git hooks
    if setup_git_hooks():
        print("✅ Git Hooks installiert")
    else:
        success = False
    
    # Test versioning script
    if test_versioning():
        print("✅ Versionierungs-Script getestet")
    else:
        success = False
    
    if success:
        print("\n🎉 Setup erfolgreich abgeschlossen!")
        show_usage_info()
    else:
        print("\n❌ Setup hatte Probleme. Bitte prüfe die Fehlermeldungen oben.")
        sys.exit(1)

if __name__ == "__main__":
    main()
