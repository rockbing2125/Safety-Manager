@echo off
REM 切换到脚本所在目录
cd /d "%~dp0"
start "" python run.py
exit