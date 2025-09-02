:: filepath: c:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\start_app.bat
@echo off
:: Navigate to the directory containing app.py
cd /d c:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation

:: Start the app.py using Python
python app.py

cd /d c:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer

:: Call run_emailer.bat before pause
call run_emailer.bat

:: Pause to keep the command prompt open in case of errors
pause