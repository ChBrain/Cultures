@echo off
REM Setup pre-commit hook for Cultures validation

setlocal enabledelayedexpansion

set HOOK_SOURCE=.githooks\pre-commit
set HOOK_TARGET=.git\hooks\pre-commit

if not exist "%HOOK_SOURCE%" (
    echo X Hook source not found: %HOOK_SOURCE%
    exit /b 1
)

echo Installing pre-commit hook...

if not exist ".git\hooks" mkdir .git\hooks

copy "%HOOK_SOURCE%" "%HOOK_TARGET%" >nul

echo + Pre-commit hook installed at %HOOK_TARGET%
echo.
echo Now run:
echo   git config core.hooksPath .githooks
