@echo off
REM Run the Open Scheduler app (Windows)
SETLOCAL
REM Set PROJECT_ROOT to the folder containing this script
SET PROJECT_ROOT=%~dp0
echo Project root: %PROJECT_ROOT%

REM If a local .venv exists, try to activate it (cmd activation)
IF EXIST "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
	echo Activating .venv
	call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
	python -m backend.app
	goto :EOF
)

REM If running from PowerShell and only Activate.ps1 exists, instruct the user
IF EXIST "%PROJECT_ROOT%\.venv\Scripts\Activate.ps1" (
	echo PowerShell virtualenv activation script found. To use it, run:
	echo   .\ .venv\Scripts\Activate.ps1
	echo Then run: python -m backend.app
	REM Fallthrough: attempt to run python from current environment
)

python -m backend.app
ENDLOCAL
