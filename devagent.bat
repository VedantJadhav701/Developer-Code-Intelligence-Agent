@echo off
REM Get the directory of this batch file
set AGENT_DIR=%~dp0
REM Run using the current python environment
python "%AGENT_DIR%devagent.py" %*
