#!/usr/bin/env python3
"""
Automatic Version Update Script
===============================

This script automatically increments the version number in paketbox.py
and updates it based on commit types (semantic versioning).

Usage:
  python update_version.py [major|minor|patch]
  
If no argument is provided, it defaults to patch increment.
"""

import re
import sys
import os
from pathlib import Path

def read_current_version(file_path):
    """Read the current version from the specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find version line with pattern: # Version X.Y.Z
        version_match = re.search(r'# Version (\d+)\.(\d+)\.(\d+)', content)
        if version_match:
            major, minor, patch = map(int, version_match.groups())
            return major, minor, patch, content
        else:
            print("Version nicht gefunden in der Datei!")
            return None
    except FileNotFoundError:
        print(f"Datei {file_path} nicht gefunden!")
        return None
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        return None

def update_version(content, old_version, new_version):
    """Update the version string in the content."""
    old_version_str = f"# Version {old_version[0]}.{old_version[1]}.{old_version[2]}"
    new_version_str = f"# Version {new_version[0]}.{new_version[1]}.{new_version[2]}"
    
    updated_content = content.replace(old_version_str, new_version_str)
    return updated_content

def write_updated_file(file_path, content):
    """Write the updated content back to the file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei: {e}")
        return False

def increment_version(major, minor, patch, increment_type='patch'):
    """Increment version based on type."""
    if increment_type == 'major':
        return major + 1, 0, 0
    elif increment_type == 'minor':
        return major, minor + 1, 0
    elif increment_type == 'patch':
        return major, minor, patch + 1
    else:
        print(f"Unbekannter Increment-Typ: {increment_type}")
        return major, minor, patch

def detect_version_increment_from_git():
    """Detect version increment type from git commit messages."""
    import subprocess
    
    try:
        # Get the last commit message
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%s'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            commit_message = result.stdout.lower()
            
            # Check for breaking changes or major version indicators
            if 'breaking change' in commit_message or 'major:' in commit_message:
                return 'major'
            # Check for new features
            elif 'feat:' in commit_message or 'feature:' in commit_message:
                return 'minor'
            # Default to patch for fixes, docs, refactor, etc.
            else:
                return 'patch'
        else:
            print("Konnte Git-Commit-Message nicht abrufen, verwende 'patch'")
            return 'patch'
            
    except FileNotFoundError:
        print("Git nicht gefunden, verwende 'patch'")
        return 'patch'
    except Exception as e:
        print(f"Fehler beim Abrufen der Git-Informationen: {e}, verwende 'patch'")
        return 'patch'

def main():
    """Main function to update version."""
    script_dir = Path(__file__).parent
    paketbox_file = script_dir / "paketbox.py"
    
    # Determine increment type
    if len(sys.argv) > 1:
        increment_type = sys.argv[1].lower()
        if increment_type not in ['major', 'minor', 'patch']:
            print("Verwendung: python update_version.py [major|minor|patch]")
            sys.exit(1)
    else:
        # Auto-detect from git commit message
        increment_type = detect_version_increment_from_git()
    
    # Read current version
    version_info = read_current_version(paketbox_file)
    if not version_info:
        sys.exit(1)
    
    major, minor, patch, content = version_info
    old_version = (major, minor, patch)
    
    # Calculate new version
    new_version = increment_version(major, minor, patch, increment_type)
    
    print(f"Aktuelle Version: {old_version[0]}.{old_version[1]}.{old_version[2]}")
    print(f"Neue Version: {new_version[0]}.{new_version[1]}.{new_version[2]} ({increment_type} increment)")
    
    # Update content
    updated_content = update_version(content, old_version, new_version)
    
    # Write updated file
    if write_updated_file(paketbox_file, updated_content):
        print(f"Version erfolgreich aktualisiert in {paketbox_file}")
        
        # Stage the file for git if in a git repository
        try:
            import subprocess
            result = subprocess.run(['git', 'add', str(paketbox_file)], 
                                  capture_output=True, 
                                  cwd=script_dir)
            if result.returncode == 0:
                print("Datei für Git-Commit vorgemerkt")
        except:
            pass  # Git not available or not in a git repo
            
    else:
        print("Fehler beim Aktualisieren der Version")
        sys.exit(1)

if __name__ == "__main__":
    main()
