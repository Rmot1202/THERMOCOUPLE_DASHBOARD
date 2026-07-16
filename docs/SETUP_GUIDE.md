# Setup Guide

Quick installation and configuration guide for the Thermocouple Dashboard.

---

## Prerequisites

- Python 3.8+ or newer
- Git
- Linux or Windows development environment
- MCC thermocouple device optional; simulator mode is available when hardware is not connected
- Docker and Docker Compose optional for containerized deployment
- On Linux, MCC support uses `uldaq` / `libuldaq` when working with supported MCC hardware

---

## Local Installation

### 1. Clone and Install Dependencies

#### Windows

```powershell
cd C:\path\to\Thermocouple_dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Ubuntu

```bash
cd ~/Desktop/Thermocouple_dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Hardware (Optional)

Edit `appilcation/config.py` and set the device IP and defaults used by the application.

Example:

```python
DEVICE_IP = "192.168.10.101"
DEFAULT_FURNACE_NUMBER = 1
DEFAULT_SETPOINT = 75.0
DEFAULT_LOWER_BOUND = 70.0
DEFAULT_UPPER_BOUND = 80.0
DEFAULT_SAMPLING_FREQUENCY = 1.0
```

The app reads `DEVICE_IP` from `config.py`, uses `sampling_frequency` to control the update interval, and stores runtime configuration in `storage/profiles/current_config.json`. [file:480]

### 3. Run the Application

#### Windows

```powershell
python appilcation/app.py
```

#### Ubuntu

```bash
python appilcation/app.py
```

Open your browser to:

```text
http://localhost:8050/
```

The Dash app runs on port 8050 in local development and exposes the WSGI server as `app.server` for Gunicorn deployment. [file:480]

---

## Ubuntu Production Setup

This is the recommended Linux deployment path for a persistent dashboard service.

### 1. Install System Packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx
```

If your MCC device requires Linux runtime support, install the MCC UL for Linux stack as needed for your hardware model, including `libuldaq` and the Python `uldaq` package.

### 2. Create Virtual Environment

```bash
cd ~/Desktop/Thermocouple_dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 3. Test the App Manually

```bash
python appilcation/app.py
```

Confirm the dashboard loads at `http://127.0.0.1:8050/`.

### 4. Test Gunicorn Manually

```bash
gunicorn --chdir /home/CCAM/raven.mott/Desktop/Thermocouple_dashboard/appilcation --workers 1 --bind 127.0.0.1:8050 app:server
```

This works because the application exposes `server = app.server` inside `app.py`. [file:480]

For hardware-connected setups, start with `--workers 1` so a single process owns the MCC device connection.

### 5. Create systemd Service

Create:

```bash
sudo nano /etc/systemd/system/thermocouple-dashboard.service
```

Paste:

```ini
[Unit]
Description=Gunicorn for Thermocouple Dashboard
After=network.target

[Service]
User=raven.mott
WorkingDirectory=/home/CCAM/raven.mott/Desktop/Thermocouple_dashboard
Environment="PATH=/home/CCAM/raven.mott/Desktop/Thermocouple_dashboard/venv/bin"
ExecStart=/home/CCAM/raven.mott/Desktop/Thermocouple_dashboard/venv/bin/gunicorn --chdir /home/CCAM/raven.mott/Desktop/Thermocouple_dashboard/appilcation --workers 1 --bind 127.0.0.1:8050 app:server
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable thermocouple-dashboard
sudo systemctl start thermocouple-dashboard
sudo systemctl status thermocouple-dashboard
```

Useful logs:

```bash
sudo journalctl -u thermocouple-dashboard -f
```

### 6. Configure NGINX Reverse Proxy

Create:

```bash
sudo nano /etc/nginx/sites-available/thermocouple-dashboard
```

Paste:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/thermocouple-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Then access the dashboard at:

```text
http://<your-server-ip>/
```

### 7. Optional HTTPS with NGINX

Install OpenSSL if needed:

```bash
sudo apt install -y openssl
```

Create a self-signed certificate:

```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -newkey rsa:2048 -keyout /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

Update the NGINX site:

```nginx
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
    }
}
```

Reload NGINX:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Then access:

```text
https://<your-server-ip>/
```

---

## Docker Setup

### 1. Build Container

```powershell
docker-compose build
```

or:

```bash
docker compose build
```

### 2. Create Storage Directories

If you are not relying on Docker-managed volumes, create the storage paths expected by the app:

```bash
mkdir -p storage/recordings
mkdir -p storage/profiles
mkdir -p storage/logs
```

The application creates and uses `storage/recordings` and `storage/profiles` by default unless `STORAGE_PATH` is overridden. [file:480]

### 3. Run Container

```powershell
docker-compose up
```

or:

```bash
docker compose up
```

Access at the port defined by your compose configuration.

---

## HTTPS Deployment with Docker

### 1. Generate Self-Signed Certificate

```bash
mkdir -p ssl
openssl req -x509 -newkey rsa:2048 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

### 2. Update `docker-compose.yml`

Ensure the SSL files are mounted into the NGINX container:

```yaml
volumes:
  - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem:ro
  - ./ssl/key.pem:/etc/nginx/ssl/key.pem:ro
```

### 3. Deploy

```bash
docker compose up -d
```

Access at:

```text
https://localhost/
```

Accept the self-signed certificate warning in your browser.

---

## Configuration

### Application Settings

The dashboard exposes a furnace/profile configuration workflow in the UI and stores active settings in JSON. [file:480]

Common settings include:

- Furnace ID
- Furnace number
- Setpoint
- Lower bound
- Upper bound
- Y-axis min and max
- Sampling frequency

These values are read into the app on startup and can be persisted to:

```text
storage/profiles/current_config.json
```

[file:480]

### Environment Variables

Create an optional `.env` file in the project root to override storage or proxy-related settings:

```env
STORAGE_PATH=./storage
DASH_BASE_PATHNAME=/
```

`STORAGE_PATH` changes the base runtime storage directory, while `DASH_BASE_PATHNAME` controls the Dash base path used when serving behind a reverse proxy. [file:480]

---

## Data Storage

### Recordings

Temperature data is written to:

```text
$STORAGE_PATH/recordings/
```

or locally:

```text
./storage/recordings/
```

The app writes TUS-style text files while recording is active. [file:480]

### Configuration

Profiles and current configuration are stored in:

```text
$STORAGE_PATH/profiles/
```

or locally:

```text
./storage/profiles/
```

The current active configuration file is:

```text
storage/profiles/current_config.json
```

[file:480]

Example JSON:

```json
{
  "furnace_id": "1",
  "furnace_number": 1,
  "setpoint": 75.0,
  "lower_bound": 70.0,
  "upper_bound": 80.0,
  "y_min": 60.0,
  "y_max": 90.0,
  "sampling_frequency": 1.0
}
```

---

## Hardware Testing

### Test MCC Device Connection

#### Windows

```powershell
.\.venv\Scripts\python.exe tests/test_hardware.py
```

#### Ubuntu

```bash
./venv/bin/python tests/test_hardware.py
```

If the MCC hardware and library are available, the test should report live readings. If the device is offline or the Linux library is unavailable, the app may fall back to simulation mode.

### Simulator Mode

If the MCC device is unavailable, the app can use simulated data so the dashboard and recording workflow remain testable. [file:480]

---

## Startup Behavior

### Local Startup

```bash
python appilcation/app.py
```

When run this way, the app starts the built-in Dash server on port 8050. [file:480]

### Service Startup

```bash
sudo systemctl start thermocouple-dashboard
sudo systemctl enable thermocouple-dashboard
```

### Check Health

```bash
sudo systemctl status thermocouple-dashboard
sudo journalctl -u thermocouple-dashboard -f
curl http://127.0.0.1:8050
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8050 already in use | Stop the conflicting process or change the bind port |
| Gunicorn starts but dashboard shows simulated data | Ensure hardware connection happens outside `__main__`, and test with `--workers 1` |
| Device not found | Verify IP address in `config.py`, network connectivity, and MCC Linux runtime setup |
| Wrong readings | Verify thermocouple type, wiring, and channel assignment |
| systemd fails with USER or GROUP errors | Correct `User=` and remove or fix `Group=` in the unit file |
| NGINX returns 502 Bad Gateway | Check that Gunicorn is running on `127.0.0.1:8050` |
| HTTPS certificate warning | Expected when using a self-signed certificate |
| Recording file empty | Let at least one sampling interval pass before stopping recording |

---

## Next Steps

1. Verify MCC hardware connectivity with the hardware test script.
2. Run the app locally and confirm live or simulated data appears.
3. Validate Gunicorn manually.
4. Configure systemd startup.
5. Add NGINX as a reverse proxy.
6. Enable HTTPS if the deployment requires encrypted browser access.

---

## Support

- See `docs/MCC_HARDWARE_GUIDE.md` for MCC device notes and Linux library references
- See `docs/SIMPLIFIED_ARCHITECTURE.md` for system design
