@echo off
echo Starting DECEPTRON...
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python main.py
