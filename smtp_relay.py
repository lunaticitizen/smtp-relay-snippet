import argparse
import smtplib
from email.message import EmailMessage

parser = argparse.ArgumentParser(description="Send an email via SMTP relay")
parser.add_argument("--to", required=True, help="Recipient address")
parser.add_argument("--from", dest="sender", default="admin@mydc.uz", help="Sender address")
parser.add_argument("--subject", default="Test Subject", help="Email subject")
parser.add_argument("--content", default="Test Content", help="Email body")
args = parser.parse_args()

msg = EmailMessage()
msg["From"] = args.sender
msg["To"] = args.to
msg["Subject"] = args.subject
msg.set_content(args.content)

with smtplib.SMTP("smtp.relay.example.com", 25) as smtp:
    smtp.starttls()
    smtp.send_message(msg)
