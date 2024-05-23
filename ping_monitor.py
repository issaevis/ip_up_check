import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
check_interval = 15  # Vej sa cdo sekonda tkontrollohet
ping_attempts = 3 # Vej sa her ta provoi nese humb paketa, kjo esht qe mos tket false positive. Varet sa stabil esht serveri, se 3 her mjafton.
email_from = "mailtrap@demomailtrap.com"
email_to = "atdsample00@gmail.com"
smtp_server = "live.smtp.mailtrap.io"
smtp_port = 587
smtp_user = "api"
smtp_password = "b2acbbe27ba226e1466c9fd921ce4dca"

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(email_from, email_to, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def is_ip_up(ip, attempts):
    for _ in range(attempts):
        response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
        if response == 0:
            return True
        time.sleep(1)
    return False

def main():
    ip_address = input("Enter the IP address to ping: ")
    while True:
        if not is_ip_up(ip_address, ping_attempts):
            print(f"{ip_address} is down!")
            send_email(f"Alert: {ip_address} is down", f"The IP address {ip_address} is not responding to pings.")
        else:
            print(f"{ip_address} is up")
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
