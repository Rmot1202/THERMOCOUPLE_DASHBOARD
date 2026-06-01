# Thermocouple Dashboard
**A Python Dash web application for monitoring MCC E-TC thermocouple channels, recording temperature data, and downloading files via HTTPS.** [file:131]

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](code_of_conduct.md) [file:130]

## Initial Contributors
- Raven Mott [file:131]

## Funding
No external funding source specified in the provided files. [file:130]

---

# Project Description

## Overview
The Thermocouple Dashboard is a Python Dash web application for monitoring MCC E-TC thermocouple channels, recording temperature data, and downloading files over HTTPS. [file:131] It is intended for engineers, researchers, or operators who need live thermocouple monitoring and recording in a manufacturing or lab setting. [file:130][file:131] The system operates as a dashboard application with local development support and a Docker-based deployment option using NGINX as a reverse proxy. [file:131]

## Key Features
- Live temperature monitoring for 3 channels: Outlet, Center, and Inlet. [file:131]
- Recording management with start/stop controls and LabVIEW-compatible TUS output files. [file:131]
- File download support, persistent JSON-based configuration, and HTTPS-ready deployment with NGINX. [file:131]

## Goals
- Provide real-time thermocouple visibility from an MCC E-TC device. [file:131]
- Support reliable recording and export of furnace temperature data in a LabVIEW-compatible format. [file:131]
- Enable local development and production-style deployment with HTTPS and hardware fallback behavior. [file:131]

---

# Developer Instructions

## Requirements

### Software
- Python with dependencies installed from `requirements.txt`. [file:131]
- Dash for the web application UI. [file:131]
- Docker and Docker Compose for containerized deployment. [file:131]
- OpenSSL for generating self-signed certificates in local HTTPS setups. [file:131]

### Hardware
- MCC E-TC thermocouple device. [file:131]
- Device IP address `192.168.10.101`. [file:131]
- The application uses channels 0, 1, and 2 out of 8 available channels. [file:131]

---

## Installation

### Local Development
```powershell
pip install -r requirements.txt
python appilcation/app.py
```

Then open: `http://localhost:8050/` [file:131]

### Docker
```powershell
docker-compose up
```

Then access: `https://localhost/` using a self-signed certificate setup. [file:131]

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
``` [file:131]

---

## Configuration
Configuration is stored either in `/storage/profiles/` or in `thermocouple_config.json/`, using JSON-based settings for furnace number and temperature bounds. [file:131] The documented environment variables are `MCC_DEVICE_IP`, `DASH_PORT`, and `POLLING_INTERVAL`. [file:131]

Example configuration:
```json
{
  "furnace_number": 1,
  "setpoint": 75.0,
  "lower_bound": 70.0,
  "upper_bound": 80.0
}
``` [file:131]

Example environment file:
```text
MCC_DEVICE_IP=192.168.10.101
DASH_PORT=8050
POLLING_INTERVAL=1000
``` [file:131]

---

## Usage

### Basic Example
```powershell
python appilcation/app.py
``` [file:131]

### Expected Output
The user should see a live dashboard showing temperature values for three thermocouple channels in the browser. [file:131] Recordings are stored as TUS text files in `/storage/recordings/`, and configuration data is stored in the profile/config JSON location. [file:131]

---

## Hardware Setup
The MCC E-TC device is configured with IP address `192.168.10.101`, and the application uses three channels: 0, 1, and 2. [file:131] If the device is unavailable, the application switches to simulator mode using Gaussian noise. [file:131]

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
Configuration is stored as JSON for furnace number and bound values. [file:131]

---

## Deployment

### Local with HTTPS
1. Generate an SSL certificate:
   ```powershell
   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
   ```
2. Update `docker-compose.yml` with certificate paths. [file:131]
3. Build and deploy:
   ```powershell
   docker-compose up -d
   ```
4. Access the application at `https://localhost/`. [file:131]

### NGINX Use
The project is documented as production-ready with an NGINX reverse proxy and HTTPS support. [file:131] In this setup, NGINX sits in front of the Dash app, handling HTTPS traffic and forwarding requests to the application service defined in the deployment stack. [file:131]

---

## Documentation
- [Simplified Architecture](docs/SIMPLIFIED_ARCHITECTURE.md) — system design and data flow. [file:131]
- [Setup Guide](docs/SETUP_GUIDE.md) — installation and configuration. [file:131]
- `MCC_HARDWARE_GUIDE.md` — device specifications, as referenced in the README. [file:131]

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Device offline | App switches to simulator mode automatically. [file:131] |
| Temperature readings stuck | Check device IP `192.168.10.101` and network connectivity. [file:131] |
| Files not downloading | Ensure `/storage/recordings/` volume is mounted in Docker. [file:131] |
| HTTPS certificate warning | Expected when using a self-signed certificate locally. [file:131] |

---

## Development

### Install for Development
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
``` [file:131]

### Run Tests
```powershell
python appilcation/test_hardware.py
``` [file:131]

### Modify App
Edit `appilcation/app.py` and refresh the browser; hot reload is enabled during development. [file:131]

---

## Limitations & Assumptions
- The application depends on MCC E-TC hardware for live readings, but falls back to simulator mode if the device is unavailable. [file:131]
- Docker-based deployment assumes mounted storage directories for recordings and profiles. [file:131]
- The provided materials do not include a full license section or detailed ownership workflow. [file:130][file:131]

---

## Future Work
- Expand formal documentation using the architecture and setup guides already referenced in the project. [file:131]
- Add clearer maintainer, licensing, and contributor details to replace remaining template placeholders. [file:130][file:131]
- Extend testing and deployment notes for non-Docker production scenarios. [file:131]

---

## Contact / Ownership
Maintainer and ownership details are not fully defined in the provided template, but Raven Mott is identified as the contributor in the project materials. [file:130][file:131]

---

## Useful Links
- [Dash Documentation](https://dash.plotly.com/) [file:131]
- [CCAM](https://ccam-va.com/) [file:130]

## Commonwealth Center for Advanced Manufacturing - CCAM
[CCAM](https://ccam-va.com/) is described in the template as an IP-friendly innovation campus where industry, academia, and government collaborate to solve advanced manufacturing challenges and develop workforce pathways. [file:130]
```

## Notes

A couple things need cleanup in the merged version:
- The title in file 131 appears blank after `#`, so I used **Thermocouple Dashboard** from the body content instead.[2]
- `thermocouple_config.json/` is written like a directory in the source, but it looks like it should probably be a file path, so you may want to change that manually in the final README.[2]
- I kept the “appilcation” folder spelling because the source explicitly says the typo is intentional.[2]

I can also return this as a **cleaned final README without citations** so you can paste it directly into GitLab.