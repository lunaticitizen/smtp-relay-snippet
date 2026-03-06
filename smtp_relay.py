import smtplib
from email.message import EmailMessage
msg = EmailMessage()
msg["From"] = "sender@example.com"
msg["To"] = "recipient@example.com"
msg["Subject"] = "Test Subject"
msg.set_content("Hello, this is a plain text email.")
with smtplib.SMTP("smtp.relay.example.com", 25) as smtp:
    smtp.starttls()
    smtp.send_message(msg)
