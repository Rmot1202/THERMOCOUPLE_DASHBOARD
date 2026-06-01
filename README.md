# Thermocouple Dashboard
**A Python Dash web application for monitoring MCC E-TC thermocouple channels, recording temperature data, and downloading files via HTTPS.**

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](code_of_conduct.md) 

## Initial Contributors
- Raven Mott 

## Funding
No external funding source specified in the provided files. 

---

# Project Description

## Overview
The Thermocouple Dashboard is a Python Dash web application for monitoring MCC E-TC thermocouple channels, recording temperature data, and downloading files over HTTPS. It is intended for engineers, researchers, or operators who need live thermocouple monitoring and recording in a manufacturing or lab setting. The system operates as a dashboard application with local development support and a Docker-based deployment option using NGINX as a reverse proxy.

## Key Features
- Live temperature monitoring for 3 channels: Outlet, Center, and Inlet. 
- Recording management with start/stop controls and LabVIEW-compatible TUS output files. 
- File download support, persistent JSON-based configuration, and HTTPS-ready deployment with NGINX. 

## Goals
- Provide real-time thermocouple visibility from an MCC E-TC device. 
- Support reliable recording and export of furnace temperature data in a LabVIEW-compatible format. 
- Enable local development and production-style deployment with HTTPS and hardware fallback behavior. 

---

# Developer Instructions

## Requirements

### Software
- Python with dependencies installed from `requirements.txt`. 
- Dash for the web application UI. 
- Docker and Docker Compose for containerized deployment. 
- OpenSSL for generating self-signed certificates in local HTTPS setups. 

### Hardware
- MCC E-TC thermocouple device. [file:131]
- Device IP address `192.168.10.101`. [file:131]
- The application uses channels 0, 1, and 2 out of 8 available channels. 

---

## Installation

### Local Development
```powershell
pip install -r requirements.txt
python appilcation/app.py
```

Then open: `http://localhost:8050/` 

### Docker
```powershell
docker-compose up
```

Then access: `https://localhost/` using a self-signed certificate setup. 

---

## Project Structure

```text
Thermocouple_dashboard/
├── appilcation/                    # Main application (note: typo is intentional)
│   ├── app.py                      # Dash frontend + callbacks
│   ├── config.py                   # Configuration constants
│   ├── hardware.py                 # MCC device interface
│   ├── profiles.py                 # Profile management
│   └── test_hardware.py
│
├── storage/                        # Docker volumes (not in git)
│   ├── recordings/                 # TUS temperature files
│   ├── profiles/                   # JSON configuration
│   └── logs/
│
├── docs/
│   ├── SIMPLIFIED_ARCHITECTURE.md  # System design
│   └── SETUP_GUIDE.md              # Installation guide
│
├── Dockerfile                      # Application container
├── docker-compose.yml              # Full stack (app + nginx)
├── requirements.txt                # Python dependencies
└── README.md
``` 

---

## Configuration
Configuration is stored either in `/storage/profiles/` or in `thermocouple_config.json/`, using JSON-based settings for furnace number and temperature bounds. [file:131] The documented environment variables are `MCC_DEVICE_IP`, `DASH_PORT`, and `POLLING_INTERVAL`. 

Example configuration:
```json
{
  "furnace_number": 1,
  "setpoint": 75.0,
  "lower_bound": 70.0,
  "upper_bound": 80.0
}
``` 

Example environment file:
```text
MCC_DEVICE_IP=192.168.10.101
DASH_PORT=8050
POLLING_INTERVAL=1000
``` 

---

## Usage

### Basic Example
```powershell
python appilcation/app.py
``` 

### Expected Output
The user should see a live dashboard showing temperature values for three thermocouple channels in the browser.Recordings are stored as TUS text files in `/storage/recordings/`, and configuration data is stored in the profile/config JSON location. 

---

## Hardware Setup
The MCC E-TC device is configured with IP address `192.168.10.101`, and the application uses three channels: 0, 1, and 2. If the device is unavailable, the application switches to simulator mode using Gaussian noise.

---

## File Formats

### TUS Format
Temperature recording files are stored in `/storage/recordings/` using the naming pattern:

```text
TUS_F{furnace}_{YYMMDD}_{HHMM}.txt
``` [file:131]

Columns are tab-separated:

```text
hour    minute  second  channel_0   channel_1   channel_2
``` [file:131]

Example:
```text
14  23  45  75.123  76.456  74.890
14  23  46  75.145  76.478  74.912
``` [file:131]

### Configuration Format
Configuration is stored as JSON for furnace number and bound values. 

---

## Deployment

### Local with HTTPS
1. Generate an SSL certificate:
   ```powershell
   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
   ```
2. Update `docker-compose.yml` with certificate paths. 
3. Build and deploy:
   ```powershell
   docker-compose up -d
   ```
4. Access the application at `https://localhost/`.

### NGINX Use
The project is documented as production-ready with an NGINX reverse proxy and HTTPS support. In this setup, NGINX sits in front of the Dash app, handling HTTPS traffic and forwarding requests to the application service defined in the deployment stack. 

---

## Documentation
- [Simplified Architecture](docs/SIMPLIFIED_ARCHITECTURE.md) — system design and data flow. 
- [Setup Guide](docs/SETUP_GUIDE.md) — installation and configuration. 
- `MCC_HARDWARE_GUIDE.md` — device specifications, as referenced in the README. 

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Device offline | App switches to simulator mode automatically.  |
| Temperature readings stuck | Check device IP `192.168.10.101` and network connectivity.  |
| Files not downloading | Ensure `/storage/recordings/` volume is mounted in Docker.  |
| HTTPS certificate warning | Expected when using a self-signed certificate locally.  |

---

## Development

### Install for Development
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
``` 

### Run Tests
```powershell
python appilcation/test_hardware.py
``` 

### Modify App
Edit `appilcation/app.py` and refresh the browser; hot reload is enabled during development. 

---

## Limitations & Assumptions
- The application depends on MCC E-TC hardware for live readings, but falls back to simulator mode if the device is unavailable.
- Docker-based deployment assumes mounted storage directories for recordings and profiles.
- The provided materials do not include a full license section or detailed ownership workflow. 

---

## Future Work
- Expand formal documentation using the architecture and setup guides already referenced in the project. 
- Add clearer maintainer, licensing, and contributor details to replace remaining template placeholders. 
- Extend testing and deployment notes for non-Docker production scenarios. 

---

## Contact / Ownership
Maintainer and ownership details are not fully defined in the provided template, but Raven Mott is identified as the contributor in the project materials.

---

## Useful Links
- [Dash Documentation](https://dash.plotly.com/) 
- [CCAM](https://ccam-va.com/) 

## Commonwealth Center for Advanced Manufacturing - CCAM
[CCAM](https://ccam-va.com/) is described in the template as an IP-friendly innovation campus where industry, academia, and government collaborate to solve advanced manufacturing challenges and develop workforce pathways. 
```
