import os
import asyncio
import csv
import tkinter as tk
from tkinter import ttk
from threading import Thread

# Configuration
check_interval = 15
ping_attempts = 3
csv_file = 'ip_list.csv'

async def is_ip_up(ip, attempts):
    for _ in range(attempts):
        process = await asyncio.create_subprocess_shell(
            f"ping -c 1 {ip} > /dev/null 2>&1",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        if process.returncode == 0:
            return True
        await asyncio.sleep(1)
    return False

class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Monitor")

        self.shops = self.load_shops_from_csv(csv_file)
        self.monitoring = False
        self.previous_statuses = {shop['name']: None for shop in self.shops}

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        self.second_frame = ttk.Frame(main_frame)
        self.second_frame.pack(padx=10, pady=10)

        self.start_button = ttk.Button(main_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(main_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status_labels = {}

        num_columns = min(len(self.shops), 12)
        for idx, shop in enumerate(self.shops):
            row = idx // num_columns
            col = idx % num_columns
            label = ttk.Label(self.second_frame, text=f"{shop['name']}")
            label.grid(row=row, column=col*2, padx=(5, 10), pady=5, sticky='w')
            status_canvas = tk.Canvas(self.second_frame, width=20, height=20, highlightthickness=0)
            status_canvas.grid(row=row, column=col*2 + 1, padx=(0, 10), pady=5, sticky='w')
            self.status_labels[shop['name']] = status_canvas

    def load_shops_from_csv(self, filename):
        shops = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                shops.append({'name': row['SHOP NAME'], 'ip': row['SHOP IP']})
        return shops

    def start_monitoring(self):
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        for shop in self.shops:
            self.status_labels[shop['name']].create_rectangle(0, 0, 20, 20, fill="grey")
        Thread(target=self.run_monitor).start()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        for shop in self.shops:
            self.status_labels[shop['name']].create_rectangle(0, 0, 20, 20, fill="grey")

    def run_monitor(self):
        asyncio.run(self.monitor())

    async def monitor(self):
        while self.monitoring:
            tasks = []
            for shop in self.shops:
                tasks.append(self.check_status(shop))
            await asyncio.gather(*tasks)
            await asyncio.sleep(check_interval)

    async def check_status(self, shop):
        current_status = await is_ip_up(shop['ip'], ping_attempts)

        if current_status != self.previous_statuses[shop['name']]:
            color = "green" if current_status else "red"
            self.status_labels[shop['name']].delete("status_indicator")
            self.status_labels[shop['name']].create_rectangle(0, 0, 20, 20, fill=color, tags="status_indicator")
            self.previous_statuses[shop['name']] = current_status

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerMonitorApp(root)
    root.mainloop()
