import smtplib
import argparse
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import os


def main():
    parser = argparse.ArgumentParser(description='Generic Emailer with Attachment and HTML body (CSV version)')
    parser.add_argument('--csv', required=True, help='Path to CSV file with email addresses')
    parser.add_argument('--emailcol', default='email', help='Column name in CSV with email addresses (default: email)')
    parser.add_argument('--fromaddr', required=True, help='Sender email address')
    parser.add_argument('--password', required=True, help='Sender email password')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--resume', required=True, help='Path to attachment file')
    parser.add_argument('--filename', required=True, help='Attachment filename as sent')
    parser.add_argument('--html', required=True, help='Path to HTML file for email body')
    parser.add_argument('--text', default='Please see the attached file.', help='Plain text fallback body')

    args = parser.parse_args()

    # Load HTML content
    if not os.path.exists(args.html):
        print(f"HTML file not found: {args.html}")
        sys.exit(1)
    with open(args.html, 'r', encoding='utf-8') as f:
        html = f.read()

    # Load CSV and get emails
    if not os.path.exists(args.csv):
        print(f"CSV file not found: {args.csv}")
        sys.exit(1)
    with open(args.csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            toaddr = row.get(args.emailcol)
            if not toaddr or str(toaddr).strip().lower() == args.emailcol.lower():
                continue
            print(f"Sending from {args.fromaddr} to: {toaddr}")

            msg = MIMEMultipart('alternative')
            msg['From'] = args.fromaddr
            msg['To'] = toaddr
            msg['Subject'] = args.subject

            part1 = MIMEText(args.text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Attachment
            if not os.path.exists(args.resume):
                print(f"Attachment file not found: {args.resume}")
                continue
            with open(args.resume, "rb") as attachment:
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename= {args.filename}")
            msg.attach(p)

            try:
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(args.fromaddr, args.password)
                s.sendmail(args.fromaddr, toaddr, msg.as_string())
                s.quit()
                print(f"Email sent to {toaddr}")
                print("" + "="*50)
            except Exception as e:
                print(f"Failed to send email to {toaddr}: {e}")

if __name__ == "__main__":
    main()

# python app.py ^
#     --csv "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\emails.csv" ^
#     --emailcol "Email" ^
#     --fromaddr "sgshelke91@gmail.com" ^
#     --password "ziistjwtnvkzujww" ^
#     --subject "Immediate Available - Java | Back-End | Software Engineer Role - Supriya Shelke" ^
#     --resume "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\data\saman\Md_Saman_Resume.pdf" ^
#     --filename "SupriyaShelke_Resume.pdf" ^
#     --html "C:\Users\epost\OneDrive\Desktop\POC\sam-cli-mf-tracker\gt-linkedin-automation\ind_emailers\generic_emailer\data\supriya\index.html" ^
#     --text "Please see the attached file."