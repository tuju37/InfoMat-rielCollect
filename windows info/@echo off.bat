@echo off
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\python 2\python-3.14.0b1-embed-amd64\python.exe"
set "SCRIPT1=%~dp0windows info.py"
set "SCRIPT2=%~dp0..\python 2\python-3.14.0b1-embed-amd64\windows info.py"

REM Cherche d'abord dans le dossier courant, sinon dans le dossier Python
if exist "%SCRIPT1%" (
    set "SCRIPT=%SCRIPT1%"
) else if exist "%SCRIPT2%" (
    set "SCRIPT=%SCRIPT2%"
) else (
    echo Le script windows info.py est introuvable.
    pause
    exit /b 1
)

"%PYTHON_EXE%" "%SCRIPT%"
pause
