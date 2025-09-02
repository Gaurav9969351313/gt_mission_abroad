

@echo off
REM Get today's date in dd-MM-yyyy format
for /f "tokens=2 delims==." %%I in ('"wmic os get localdatetime /value"') do set dt=%%I
set today=%dt:~6,2%-%dt:~4,2%-%dt:~0,4%


REM List of CSV base names to process
setlocal enabledelayedexpansion
set lists=hiring_for_freshers_emails hiring_for_java_dubai_emails hiring_for_java_remote_emails java_contract_remote_emails java_remote_WFH_emails java_freelance_remote_emails hiring_for_qa_emails

for %%L in (%lists%) do (
  echo Sending emails using list: %%L
  python app.py ^
    --csv "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\extract\%today%\%%L.csv" ^
    --emailcol "Email" ^
    --fromaddr "tejalsarode29@gmail.com" ^
    --password "nsjmwrpocvkogbqb" ^
    --subject "Java Developer - Resume: Tejal Sarode" ^
    --resume "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\data\teju\cv_2YoE_Java_Developer_TejalSarode.pdf" ^
    --filename "cv_2YoE_Java_Developer_TejalSarode.pdf" ^
    --html "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\data\teju\index.html" ^
    --text "Please see the attached file."

  python app.py ^
    --csv "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\extract\%today%\%%L.csv" ^
    --emailcol "Email" ^
    --fromaddr "samtrade15@gmail.com" ^
    --password "vkldmttncltfhbin" ^
    --subject "Application - Java | Back-End | Software Developer Role" ^
    --resume "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\data\saman\Md_Saman_Resume.pdf" ^
    --filename "Md_Saman_Resume.pdf" ^
    --html "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\data\saman\index.html" ^
    --text "Please see the attached file."

  
  echo ------------------------------------------------------------------------------
)

echo "------------------------------------------------------------------------------------"

pause

