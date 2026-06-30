@echo off
echo ========================================
echo  SCARICAMENTO CAMPIONATI
echo ========================================
echo.

REM Attiva virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment attivato
) else (
    echo ATTENZIONE: Virtual environment non trovato!
    echo Crealo con: python -m venv venv
    pause
    exit /b 1
)

REM Installa dipendenze se necessario
python -c "import requests" 2>nul || pip install requests pandas openpyxl

REM Esegui lo script
python campionati.py

echo.
echo ========================================
echo  PREM