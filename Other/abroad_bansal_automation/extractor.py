import csv
from datetime import datetime
import os
import re

from PyPDF2 import PdfReader

file_name = "PaidExperiencedJob_25-8-2025_ALL_JOBS.pdf"
DOWNLOAD_FOLDER = "downloads"

# --- Ensure download directory exists ---
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}\b"

all_emails = set()

pdf_path = os.path.join(DOWNLOAD_FOLDER, file_name)
with open(pdf_path, 'rb') as pdf_file:
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    found_emails = re.findall(email_pattern, text)
    print(f"📧 Emails found in {file_name}:")
    for email_id in found_emails:
        all_emails.add(email_id)

if all_emails:
        extract_folder = 'extract'
        os.makedirs(extract_folder, exist_ok=True)
        date_str = datetime.now().strftime('%d-%m-%Y')
        csv_filename = f"extracted_emails_{date_str}.csv"
        csv_path = os.path.join(extract_folder, csv_filename)
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Email'])
            # Collect all unique, valid emails first
            unique_emails = set()
            for email_id in all_emails:
                if (
                    '..' in email_id
                    or email_id.startswith(('.', '-'))
                    or email_id.endswith(('.', '-'))
                    or not re.match(email_pattern, email_id)
                ):
                    continue
                trimmed_email = email_id.strip()
                unique_emails.add(trimmed_email.lower())
                print(f"Valid email: {trimmed_email}")
            # Write all unique emails at once
            writer.writerows([[email] for email in sorted(unique_emails)])
        print(f"Saved {len(unique_emails)} emails to {csv_path}")