import argparse
import socket
import smtplib
from email.message import EmailMessage

parser = argparse.ArgumentParser(description="Send an email via SMTP relay")
parser.add_argument("--to", required=True, nargs="+", help="Recipient address(es)")
parser.add_argument("--from", dest="sender", default="admin@mydc.uz", help="Sender address")
parser.add_argument("--subject", default="Test Subject", help="Email subject")
parser.add_argument("--content", default="Test Content", help="Email body")
group = parser.add_mutually_exclusive_group()
group.add_argument("-4", dest="ipv4", action="store_true", help="Force IPv4")
group.add_argument("-6", dest="ipv6", action="store_true", help="Force IPv6")
args = parser.parse_args()

msg = EmailMessage()
msg["From"] = args.sender
msg["To"] = ", ".join(args.to)
msg["Subject"] = args.subject
msg.set_content(args.content)

smtp_host = "tas03smtp.mydc.uz"
smtp_port = 25

if args.ipv4 or args.ipv6:
    family = socket.AF_INET if args.ipv4 else socket.AF_INET6
    addr_info = socket.getaddrinfo(smtp_host, smtp_port, family, socket.SOCK_STREAM)
    addr = addr_info[0][4]
    with smtplib.SMTP() as smtp:
        smtp.connect(addr[0], addr[1])
        smtp.starttls()
        smtp.send_message(msg)
else:
    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.send_message(msg)
