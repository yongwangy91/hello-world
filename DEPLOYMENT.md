# Deployment Guide

This application can be deployed in two main ways: locally on your personal computer or on a Cloud VPS (Virtual Private Server).

## Option 1: Local Deployment (Easiest)
Best for personal use if you don't mind keeping your computer on for the scheduled crawl (or running it manually).

1.  **Follow the Installation steps** in `README.md`.
2.  **Run the server:**
    ```bash
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
    ```
3.  The crawler will run automatically every day at 09:00 AM (as long as the script is running).
4.  You can access the dashboard at `http://localhost:8000`.

## Option 2: Cloud VPS (Recommended for Automation)
Best for "set and forget" automation. The server runs 24/7.

**Requirements:** A small Linux VPS (e.g., DigitalOcean Droplet, AWS EC2, Vultr, Linode) - usually ~$5/month. Ubuntu 22.04 LTS is recommended.

**Steps:**

1.  **Connect to your VPS** via SSH.
2.  **Update System & Install Python/Git:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3-pip python3-venv git -y
    ```
3.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url> app
    cd app
    ```
4.  **Install Dependencies:**
    ```bash
    pip3 install -r requirements.txt
    playwright install chromium
    playwright install-deps
    ```
    *Note: `playwright install-deps` is crucial on Linux to install system libraries needed for the browser.*

5.  **Run with Systemd (Keep it running):**
    Create a service file to keep the app running in the background.
    ```bash
    sudo nano /etc/systemd/system/crawler.service
    ```
    Paste the following (adjust paths as needed):
    ```ini
    [Unit]
    Description=HK Internship Crawler
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/root/app
    ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
    Save and exit (Ctrl+X, Y, Enter).

6.  **Start the Service:**
    ```bash
    sudo systemctl enable crawler
    sudo systemctl start crawler
    ```
7.  **Access:** Open `http://<YOUR_VPS_IP>:8000` in your browser.
