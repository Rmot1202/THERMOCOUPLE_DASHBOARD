# Thermocouple Dashboard

A Python Dash web application for monitoring an MCC thermocouple device, visualizing live temperature data, recording TUS-style output files, and managing furnace profile settings. The dashboard is designed for lab and manufacturing use where operators need simple browser-based visibility into live thermocouple readings and recording controls. [file:480]

## Features

- Live temperature display for three dashboard positions: Outlet, Center, and Inlet. [file:480]
- Real-time charting of incoming temperature data with configurable bounds and setpoint lines. [file:480]
- Recording controls for starting and stopping TUS-style temperature logs. [file:480]
- Save/export workflow for recording files and furnace configuration. [file:480]
- Persistent JSON-based profile and configuration storage. [file:480]
- Simulation fallback when MCC hardware is unavailable. [file:480]

## Project Structure

```text
Thermocouple_dashboard/
├── appilcation/                  # Main application package (directory name is intentional)
│   ├── app.py                    # Dash UI, callbacks, data flow, recording logic
│   ├── config.py                 # Device IP and app defaults
│   ├── hardware.py               # MCC thermocouple interface
│   └── profiles.py               # Furnace profile management
│
├── tests/                        # Automated and manual tests
│   ├── test_app_helpers.py
│   ├── test_dash_callbacks.py
│   ├── test_hardware.py
│   ├── test_hardware_wrapper.py
│   └── test_profiles.py
│
├── storage/                      # Runtime data
│   ├── recordings/               # Saved TUS text files
│   └── profiles/                 # Current config and saved profile JSON files
│
├── docs/                         # Project documentation
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Requirements

### Software

- Python 3 with dependencies installed from `requirements.txt`.
- Dash and Dash Bootstrap Components for the web UI. [file:480]
- Plotly for live chart rendering. [file:480]
- Optional: Docker and Docker Compose for containerized deployment.
- Optional: Gunicorn and systemd for Linux service deployment.

### Hardware

- MCC thermocouple-capable DAQ device.
- Thermocouple channels read through the MCC hardware interface. [file:480]
- The UI displays channels 0, 1, and 2 as Outlet, Center, and Inlet. [file:480]
- The hardware layer can read all 8 channels and then use the first 3 for the dashboard. [file:480]
- Thermocouple type should be configured to match the installed sensor type in `hardware.py`.

## Installation

### Local Development

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the application:

```bash
python appilcation/app.py
```

Then open:

```text
http://localhost:8050/
```

### Linux Service with Gunicorn

A common production-style launch command is:

```bash
gunicorn --chdir /path/to/Thermocouple_dashboard/appilcation --workers 1 --bind 127.0.0.1:8050 app:server
```

For hardware-connected deployments, a single worker is recommended during validation so only one process talks to the MCC device at a time.

### Docker

If your repository includes a working Docker configuration, run:

```bash
docker-compose up --build
```

Then access the app according to your compose configuration.

## Configuration

The app loads defaults from `appilcation/config.py` and stores runtime configuration in JSON files under `storage/profiles/`. [file:480]

### Runtime Storage Paths

- Current configuration: `storage/profiles/current_config.json` [file:480]
- Saved profiles: `storage/profiles/*.json` [file:480]
- Recordings: `storage/recordings/` [file:480]

### Typical Configuration Values

The live app uses configuration fields including:

- `furnace_id` [file:480]
- `furnace_number` [file:480]
- `setpoint` [file:480]
- `lower_bound` [file:480]
- `upper_bound` [file:480]
- `y_min` [file:480]
- `y_max` [file:480]
- `sampling_frequency` [file:480]

Example profile JSON:

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

## Usage

### Run the Dashboard

```bash
python appilcation/app.py
```

### Dashboard Functions

The dashboard provides:

- A live temperature chart. [file:480]
- Live value cards for three displayed channels. [file:480]
- Furnace profile selection and save behavior. [file:480]
- Configurable timer and alert behavior. [file:480]
- Recording controls for temperature logging. [file:480]

### Recording Workflow

1. Start recording from the dashboard. [file:480]
2. The application writes temperature rows into a text file in `storage/recordings/`. [file:480]
3. Stop recording to finalize the session. [file:480]
4. Use the save workflow to export the latest recording and persist the active furnace configuration. [file:480]

## Hardware Behavior

The application creates an `MCCThermocouple` interface using the configured device IP, then reads live temperatures from the MCC hardware layer. [file:480] If the hardware is unavailable or not connected, the app can fall back to simulated values so the dashboard remains usable. [file:480]

### Channel Mapping in the UI

- Channel 0 → Outlet [file:480]
- Channel 1 → Center [file:480]
- Channel 2 → Inlet [file:480]

### Simulation Mode

If no live hardware connection is available, the dashboard can display simulated readings and show a simulation status/banner in the UI. [file:480]

## Recording Format

Recordings are saved as text files in `storage/recordings/`. [file:480]

The app writes rows containing time fields and channel temperatures during active recording. [file:480]

Example structure:

```text
hour    minute    second    channel_0    channel_1    channel_2    0.000
14.000  23.000    45.123    75.123       76.456       74.890       0.000
14.000  23.000    46.124    75.145       76.478       74.912       0.000
```

File names are generated automatically when recording starts. [file:480]

## Deployment Notes

### Gunicorn + systemd

For Linux deployment, the app can be served by Gunicorn and managed by systemd. The Dash server object is exposed as:

```python
server = app.server
```

which allows Gunicorn to run the app as `app:server` from the `appilcation/` directory. [file:480]

Example service command:

```bash
/home/USER/path/to/venv/bin/gunicorn --chdir /home/USER/path/to/Thermocouple_dashboard/appilcation --workers 1 --bind 127.0.0.1:8050 app:server
```

### Reverse Proxy

For internal or production environments, place NGINX in front of Gunicorn and proxy traffic to `127.0.0.1:8050`.

## Testing

Run automated tests from the repository root:

```bash
pytest -q
```

Or, if using the virtual environment Python directly:

```bash
./venv/bin/python -m pytest -q
```

Manual or hardware-focused tests can be run from the `tests/` directory depending on the available MCC device and local setup.

## Troubleshooting

| Issue | Likely Cause | Action |
|---|---|---|
| Dashboard shows simulation mode | MCC device not connected or app did not connect successfully | Verify device connectivity, IP, thermocouple type, and service startup logs. [file:480] |
| Direct Python run works but Gunicorn shows simulated data | Hardware connection code only runs in `__main__` or Gunicorn workers are not connecting correctly | Move/connect hardware during app import or retry in the read path; test with one worker. [file:480] |
| No recordings saved | Recording not started or storage path unavailable | Check `storage/recordings/` and verify write permissions. [file:480] |
| Service starts but browser is unreachable | Gunicorn bound to localhost only, or reverse proxy not configured | Check service status, local curl response, and proxy settings. |
| Wrong temperature values | Thermocouple type mismatch | Set the MCC thermocouple type in `hardware.py` to match the installed probe type. |

## Development Notes

- The application directory is named `appilcation/` and that spelling is used intentionally throughout the project structure.
- The Dash app uses `suppress_callback_exceptions=True` and a server object for Gunicorn compatibility. [file:480]
- Persistent runtime data is stored in `storage/`, not inside the source package. [file:480]
- Sampling frequency is configurable in the UI and affects the dashboard interval timing. [file:480]

## Future Improvements

- Add a dedicated environment-variable example file.
- Document the exact MCC hardware setup and thermocouple type requirements.
- Expand Docker and NGINX deployment documentation.
- Add clearer contributor, maintainer, and license sections.

## Contributor

- Raven Mott

## Useful Links

- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Documentation](https://plotly.com/python/)
- [CCAM](https://ccam-va.com/)
