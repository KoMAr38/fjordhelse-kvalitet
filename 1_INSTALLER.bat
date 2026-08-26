@echo off
chcp 65001 >nul
echo ==========================================
echo  Fjordhelse datakvalitet - installasjon
echo ==========================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
  echo FEIL: Python er ikke funnet.
  echo Installer Python og huk av "Add python.exe to PATH".
  pause
  exit /b 1
)
echo Installerer pakker. Dette tar 1-3 minutter.
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
  echo FEIL under installasjon av pakker.
  pause
  exit /b 1
)
echo.
echo Ferdig.
pause
