import argparse
import ipaddress
import socket
import sys
import smtplib
from email.message import EmailMessage

parser = argparse.ArgumentParser(description="Send an email via SMTP relay")
parser.add_argument("--to", required=True, nargs="+", help="Recipient address(es)")
parser.add_argument("--from", dest="sender", default="admin@mydc.uz", help="Sender address")
parser.add_argument("--subject", default="Test Subject", help="Email subject")
parser.add_argument("--content", default="Test Content", help="Email body")
parser.add_argument("--server", default=None, help="SMTP server DNS name, IPv4, or IPv6 address")
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

if args.server:
    smtp_host = args.server
    try:
        addr = ipaddress.ip_address(smtp_host)
        smtp_host = f"[{addr}]" if isinstance(addr, ipaddress.IPv6Address) else str(addr)
    except ValueError:
        pass  # treat as DNS name
    if args.ipv4 or args.ipv6:
        family = socket.AF_INET if args.ipv4 else socket.AF_INET6
        label = "IPv4" if args.ipv4 else "IPv6"
        try:
            addr_info = socket.getaddrinfo(args.server, smtp_port, family, socket.SOCK_STREAM)
        except socket.gaierror:
            print(f"Error: No {label} address found for {args.server}", file=sys.stderr)
            sys.exit(1)
        addr = addr_info[0][4]
        with smtplib.SMTP() as smtp:
            smtp.connect(addr[0], addr[1])
            smtp.starttls()
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls()
            smtp.send_message(msg)
elif args.ipv4 or args.ipv6:
    family = socket.AF_INET if args.ipv4 else socket.AF_INET6
    label = "IPv4" if args.ipv4 else "IPv6"
    try:
        addr_info = socket.getaddrinfo(smtp_host, smtp_port, family, socket.SOCK_STREAM)
    except socket.gaierror:
        print(f"Error: No {label} address found for {smtp_host}", file=sys.stderr)
        sys.exit(1)
    addr = addr_info[0][4]
    with smtplib.SMTP() as smtp:
        smtp.connect(addr[0], addr[1])
        smtp.starttls()
        smtp.send_message(msg)
else:
    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.send_message(msg)
