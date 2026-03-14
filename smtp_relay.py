#!/usr/bin/env python3
import argparse
import ipaddress
import socket
import ssl
import sys
import smtplib
from email.message import EmailMessage

parser = argparse.ArgumentParser(
    description="Send an email via SMTP relay",
    epilog="""
examples:
  %(prog)s --to user@example.com
  %(prog)s --to user1@example.com user2@example.com --subject "Hello"
  %(prog)s --to user@example.com --from noreply@mydc.uz --content "Body text"
  %(prog)s --to user@example.com --server mail.example.com
  %(prog)s --to user@example.com --server 10.0.0.5
  %(prog)s --to user@example.com --server fd00::1
  %(prog)s --to user@example.com -4
  %(prog)s --to user@example.com --server mail.example.com -6
  %(prog)s --to user@example.com --no-verify
""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument("--to", required=True, nargs="+", help="Recipient address(es)")
parser.add_argument("--from", dest="sender", default="admin@mydc.uz", help="Sender address (default: admin@mydc.uz)")
parser.add_argument("--subject", default="Test Subject", help="Email subject (default: Test Subject)")
parser.add_argument("--content", default="Test Content", help="Email body (default: Test Content)")
parser.add_argument("--server", default=None, help="SMTP server DNS name, IPv4, or IPv6 address (default: tas03smtp.mydc.uz)")
parser.add_argument("--no-verify", dest="no_verify", action="store_true", help="Skip TLS certificate verification")
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

tls_context = None
if args.no_verify:
    tls_context = ssl.create_default_context()
    tls_context.check_hostname = False
    tls_context.verify_mode = ssl.CERT_NONE

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
            smtp.starttls(context=tls_context)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls(context=tls_context)
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
        smtp.starttls(context=tls_context)
        smtp.send_message(msg)
else:
    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls(context=tls_context)
        smtp.send_message(msg)
