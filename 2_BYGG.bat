@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo  Fjordhelse datakvalitet - bygg
echo ==========================================
echo.
echo [1/4] Genererer syntetiske data
python src\generer_data.py
if errorlevel 1 goto feil
echo.
echo [2/4] Laster raadata inn i DuckDB
python src\last_inn_raa.py
if errorlevel 1 goto feil
echo.
echo [3/4] Bygger modell og kjoerer tester
cd dbt
python run.py build
if errorlevel 1 goto feil_dbt
cd ..
echo.
echo [4/4] Eksporterer mart
python src\eksporter_mart.py
if errorlevel 1 goto feil
echo.
echo ==========================================
echo  OK - alt bygget og testet
echo ==========================================
pause
exit /b 0

:feil_dbt
cd ..
:feil
echo.
echo ==========================================
echo  FEIL - se foerste ERROR-linje ovenfor
echo ==========================================
pause
exit /b 1
