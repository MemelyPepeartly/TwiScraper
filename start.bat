@echo off
SETLOCAL

SET "VENV=twiscrape-env"
SET "SCRIPT=TwiScraper.py"

ECHO Checking for virtual environment...
IF NOT EXIST "%VENV%\Scripts\python.exe" (
    ECHO Creating virtual environment...
    python -m venv %VENV%
) ELSE (
    ECHO Virtual environment exists.
)

ECHO Activating virtual environment...
CALL "%VENV%\Scripts\activate"

ECHO Installing dependencies...
python -m pip install requests

ECHO Running script...
python %SCRIPT%

pause
ENDLOCAL
