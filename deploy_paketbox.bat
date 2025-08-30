@echo off
REM Deployment-Script für paketbox.py auf einen Raspberry Pi via SSH (Windows-Version)
REM Usage: deploy_paketbox.bat <USER> <RASPBERRY_PI_IP> <TARGET_PATH>

set USER=%1
set RASPBERRY_PI_IP=%2
set TARGET_PATH=%3

if "%USER%"=="" goto usage
if "%RASPBERRY_PI_IP%"=="" goto usage
if "%TARGET_PATH%"=="" goto usage

REM Backup der vorhandenen Datei auf dem Raspberry Pi
plink %USER%@%RASPBERRY_PI_IP% "if [ -f '%TARGET_PATH%/paketbox.py' ]; then cp '%TARGET_PATH%/paketbox.py' '%TARGET_PATH%/paketbox.py.bak_%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%'; fi"

REM Kopiere die Datei via scp
pscp paketbox.py %USER%@%RASPBERRY_PI_IP%:%TARGET_PATH%

if %ERRORLEVEL%==0 (
    echo paketbox.py erfolgreich auf %RASPBERRY_PI_IP% kopiert.
) else (
    echo Fehler beim Kopieren!
    exit /b 2
)

exit /b 0

:usage
    echo Usage: %0 ^<USER^> ^<RASPBERRY_PI_IP^> ^<TARGET_PATH^>
    exit /b 1
