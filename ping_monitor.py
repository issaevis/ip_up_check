import os
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import messagebox

# Configuration
check_interval = 15  # Check interval in seconds
ping_attempts = 3    # Number of ping attempts
email_from = "atdsample00@gmail.com"
email_to = "evis.topollaj@gmail.com"
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "atdsample00@gmail.com"
smtp_password = "tjoydqsgpythninq"

def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(email_from, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Ping function
def is_ip_up(ip, attempts):
    for _ in range(attempts):
        response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
        if response == 0:
            return True
        time.sleep(1)
    return False

class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Monitor")

        self.ip_address = tk.StringVar()
        self.destination_email = tk.StringVar()  # Destination email address variable
        self.status = tk.StringVar()
        self.status.set("Status: Not Started")
        self.monitoring = False
        self.previous_status = None

        tk.Label(root, text="IP Address:").pack(pady=5)
        self.ip_entry = tk.Entry(root, textvariable=self.ip_address)
        self.ip_entry.pack(pady=5)

        tk.Label(root, text="Destination Email:").pack(pady=5)  # Label for destination email
        self.email_entry = tk.Entry(root, textvariable=self.destination_email)  # Entry field for destination email
        self.email_entry.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        tk.Label(root, textvariable=self.status).pack(pady=5)

    def start_monitoring(self):
        self.monitoring = True
        self.previous_status = None
        self.ip_entry.config(state=tk.DISABLED)  # Disable IP entry
        self.email_entry.config(state=tk.DISABLED)  # Disable email entry
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status.set("Status: Monitoring")
        threading.Thread(target=self.monitor).start()

    def stop_monitoring(self):
        self.monitoring = False
        self.ip_entry.config(state=tk.NORMAL)  # Enable IP entry
        self.email_entry.config(state=tk.NORMAL)  # Enable email entry
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status.set("Status: Not Monitoring")

    def monitor(self):
        ip_address = self.ip_address.get()
        destination_email = self.destination_email.get()  # Get destination email from entry field
        while self.monitoring:
            current_status = is_ip_up(ip_address, ping_attempts)

            if current_status != self.previous_status:
                if current_status:
                    self.status.set(f"Status: {ip_address} is up!")
                    send_email(f"Alert: {ip_address} is up", f"The IP address {ip_address} is now responding to pings.", destination_email)
                else:
                    self.status.set(f"Status: {ip_address} is down!")
                    send_email(f"Alert: {ip_address} is down", f"The IP address {ip_address} is not responding to pings.", destination_email)

                self.previous_status = current_status

            time.sleep(check_interval)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerMonitorApp(root)
    root.mainloop()
