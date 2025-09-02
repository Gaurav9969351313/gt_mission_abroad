@echo off
set taskname=LinkedInScrapperTask
set scriptpath=C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\app.py
set pythonpath=C:\Python312\python.exe
set workdir=C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation

:: Create a new scheduled task with arguments and working directory
schtasks /create /tn "%taskname%" /tr "cmd /c cd /d \"%workdir%\" && \"%pythonpath%\" \"%scriptpath%\" local" /sc onstart /rl highest /f /IT
@REM schtasks /create /tn "%taskname%" /tr "cmd /c cd /d \"%workdir%\" && start /b \"%pythonpath%\" \"%scriptpath%\" local" /sc onstart /rl highest /f /IT
wevtutil set-log Microsoft-Windows-TaskScheduler/Operational /enabled:true

echo Task "%taskname%" created successfully! Your Flask app will start automatically on boot with 'local' argument.
pause
