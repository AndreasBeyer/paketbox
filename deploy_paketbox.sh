#!/bin/bash
# Deployment-Script für paketbox.py auf einen Raspberry Pi via SSH
# Usage: ./deploy_paketbox.sh <USER> <RASPBERRY_PI_IP> <TARGET_PATH>

USER="$1"
RASPBERRY_PI_IP="$2"
TARGET_PATH="$3"

if [ -z "$USER" ] || [ -z "$RASPBERRY_PI_IP" ] || [ -z "$TARGET_PATH" ]; then
  echo "Usage: $0 <USER> <RASPBERRY_PI_IP> <TARGET_PATH>"
  exit 1
fi

# Backup der vorhandenen Datei auf dem Raspberry Pi
ssh "$USER@$RASPBERRY_PI_IP" "if [ -f '$TARGET_PATH/paketbox.py' ]; then cp '$TARGET_PATH/paketbox.py' '$TARGET_PATH/paketbox.py.bak_$(date +%Y%m%d_%H%M%S)'; fi"

# Kopiere die Datei via scp
scp paketbox.py "$USER@$RASPBERRY_PI_IP:$TARGET_PATH"

if [ $? -eq 0 ]; then
  echo "paketbox.py erfolgreich auf $RASPBERRY_PI_IP kopiert."
else
  echo "Fehler beim Kopieren!"
  exit 2
fi
