import imaplib
import email
import os
import re
import zipfile
import csv
from PyPDF2 import PdfReader
from datetime import datetime

import smtplib
import openpyxl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Settings --> Actions --> General --> Workflow Permissions --> Read and Write for Actions
execute_complete_workflow = False  # Set to True to enable the workflow
email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}\b"
# --- Function to process emails based on flag ---
def process_emails(flag='UNSEEN'):
    # --- Configuration ---
    EMAIL = "gaurav.cdac16@gmail.com"
    PASSWORD = "kkpkypivcbufovab"  # Use App Password if 2FA is enabled
    IMAP_SERVER = "imap.gmail.com"
    DOWNLOAD_FOLDER = "downloads"

    # --- Ensure download directory exists ---
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # --- Connect to Gmail ---
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, f'({flag})')
    email_ids = messages[0].split()
    all_emails = set()
    
    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if filename and filename.endswith('.zip'):
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print(f"Downloaded ZIP: {filepath}")
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(DOWNLOAD_FOLDER)
                print(f"Extracted ZIP: {filepath}")
                for extracted_file in zip_ref.namelist():
                    if extracted_file.endswith('.pdf'):
                        pdf_path = os.path.join(DOWNLOAD_FOLDER, extracted_file)
                        with open(pdf_path, 'rb') as pdf_file:
                            reader = PdfReader(pdf_file)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text() or ""
                            found_emails = re.findall(email_pattern, text)
                            print(f"📧 Emails found in {extracted_file}:")
                            for email_id in found_emails:
                                all_emails.add(email_id)
                print("------")
        mail.store(e_id, '+FLAGS', '\\Seen')
    mail.logout()
    return all_emails

def send_email(toaddr, resume_path, filename):
    fromaddr = "epostgauravtalele@gmail.com"
    from_add_password = "srvfifbwhujuanpp"
    # fromaddr = "gauravtalele2025@gmail.com"
    # from_add_password = "rsaxzwrxcqlzhkbh"

    email_subject = "Job Application For Sr. Java Developer (Full Stack) | 8.5 - YoE | NP Serving | Gaurav Talele"
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = email_subject

    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """
    <html>
    <body style=" font-family: Arial, Helvetica, sans-serif; font-size: 22px">
        <h4>Dear Hiring Manager,</h4>
        <h5>I hope you are doing well. <h5>
                <p style="font-weight: normal; line-height: 24px">
                    I am writing to express my strong interest in being the next Sr. Full Stack Developer at your
                    organisation. As an ambitious professional with almost <b>8.5 years of experience</b> in <b>Java, Spring
                        Boot, Angular, Apache Camel, Apache Kafka, Microservices, Axon, Oracle, Jasper Reports, Git, Docker,
                        Docker Compose, CICD, AWS</b>. <br>
                    I believe that I would make an excellent addition to your team. I am currently working as a Senior Java
                    Full Stack Engineer with Bank Of New York Mellon.<br>
                    I have attached my CV hoping that you will consider me for the place in your organisation, should you
                    need more details or references I can supply those at your convenience. Otherwise <b>I would like to
                        have an interview</b> and talk more about being a new employee for your esteemed
                    Organisation.<br><br>
                <table style="font-weight: normal; line-height: 24px;" border=1>
                    <tr>
                        <td style="font-weight: bold;">First Name</td>
                        <td>Gaurav</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Middle Name</td>
                        <td>Yashwant</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Last Name</td>
                        <td>Talele</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Date Of Birth</td>
                        <td>11/02/1994</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Location Preferences</td>
                        <td>Dubai / Singapore </td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Notice Period</td>
                        <td>45 Days</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Last Working Day</td>
                        <td>15/10/2025</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Nationality</td>
                        <td>Indian</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Current City</td>
                        <td>Mumbai, India</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Open For</td>
                        <td>Remote / Hybrid</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Total Relevant YoE</td>
                        <td>8.5 Years</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">PAN Number</td>
                        <td>AUDPT4503C</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Reason for Job Change</td>
                        <td>Looking For better opputunity</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Heighest Qualification</td>
                        <td>Bachelor Of Engineering + PGDAC</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Current Company</td>
                        <td>Bank Of New York Mellon (BNY)</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Current Designation</td>
                        <td>Sr. Java Full Stack Engineer</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Experience</td>
                        <td>
                            <table style="font-weight: normal; line-height: 24px;" border=1>
                                <tr>
                                    <td style="font-weight: bold;">Java, Spring Boot</td>
                                    <td>8.5 Years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">Angular</td>
                                    <td>5 Years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">Microservices</td>
                                    <td>4 Years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">Apach Camel</td>
                                    <td>4 years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">Apache Kafka, IBM MQ</td>
                                    <td>4 years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">Oracle, MongoDB, Redis</td>
                                    <td>5 years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">Docker, Kubernetes</td>
                                    <td>5 years</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold;">AWS</td>
                                    <td>4 years</td>
                                </tr>
                                
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">Linked In Profile</td>
                        <td>https://www.linkedin.com/in/gaurav9969351313/</td>
                    </tr>
                   
                    <tr>
                        <td style="font-weight: bold;">Alternate Email ID</td>
                        <td>epostgauravtalele@gmail.com</td>
                    </tr>
                </table>
                <br>
                <br>
                Thank you for your time and consideration. .. :)
                </p>
                <br>
                <p style="line-height: 24px">With Best Regards,<br></p>
                <p style="line-height: 22px; font-weight: normal;">
                    Mr. Gaurav Talele <br>
                    <b>Sr. Java Full Stack Engineer (SDE-2)</b><br>
                    [M]: gauravtalele2025@gmail.com<br>
                    [H]: +91-9969351313
                    <br>
                </p>
    </body>
    </html>
    """
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    try:
        with open(resume_path, "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename= %s" % filename)
            msg.attach(p)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, from_add_password)
        s.sendmail(fromaddr, toaddr, msg.as_string())
        s.quit()
        print(f"Sent email to {toaddr}")
    except Exception as e:
        print(f"Failed to send email to {toaddr}: {e}")

# --- Use the function to process emails ---

if execute_complete_workflow:
    all_emails = process_emails(flag='UNSEEN')
    # --- Write all emails to CSV in extract folder with timestamp ---
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

# --- Send emails based on the extracted file ---
extract_folder = 'extract'
date_str = datetime.now().strftime('%d-%m-%Y')
csv_filename = f"extracted_emails_{date_str}.csv"
csv_path = os.path.join(extract_folder, csv_filename)

if os.path.exists(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            to_add = row['Email']
            resume_path = "./cv_Sr_Java_Full_Stack_GauravTalele-8-YoE.docx"
            filename = "cv_Sr_Java_Full_Stack_GauravTalele-8-YoE.docx"
            send_email(to_add, resume_path, filename)
