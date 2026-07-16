import time

try:
    import uldaq as ul
except Exception:
    ul = None


class MCCThermocouple:
    def __init__(self, device_ip="192.168.0.101", board_num=0):
        self.device_ip = device_ip
        self.board_num = board_num
        self.connected = False
        self.device = None
        self.ai_device = None
        self.last_error = None
        self.simulation_mode = False
        self._last_logged_error = None
        self.ever_had_real_data = False
        self.last_real_data_ts = None
        self.scale = ul.TempScale.CELSIUS if ul else None
        self.thermocouple_type = ul.TcType.R if ul else None

        if ul is None:
            self.last_error = "uldaq library unavailable"
            self._log_once(self.last_error)

    def _log_once(self, message):
        if message != self._last_logged_error:
            print(message)
            self._last_logged_error = message

    def _simulate(self, count):
        try:
            import numpy as np
            noise = np.random.normal(0, 0.5, count)
            return [72.5 + (2.0 * idx) + noise[idx] for idx in range(count)]
        except Exception:
            import random
            return [72.5 + (2.0 * idx) + random.gauss(0, 0.5) for idx in range(count)]

    def _mark_real_data(self):
        self.ever_had_real_data = True
        self.last_real_data_ts = time.time()
        self.simulation_mode = False

    def connect(self):
        if ul is None:
            self.connected = False
            self.simulation_mode = True
            self.last_error = "uldaq library not available. Using simulation mode."
            self._log_once(self.last_error)
            return False

        try:
            devices = ul.get_daq_device_inventory(ul.InterfaceType.ETHERNET)
            if not devices:
                devices = ul.get_daq_device_inventory(ul.InterfaceType.ANY)

            if not devices:
                self.connected = False
                self.simulation_mode = True
                self.last_error = "No MCC device found."
                self._log_once(self.last_error)
                return False

            chosen = None
            for d in devices:
                if self.device_ip and self.device_ip in str(d):
                    chosen = d
                    break
            if chosen is None:
                chosen = devices[0]

            self.device = ul.DaqDevice(chosen)
            self.device.connect(connection_code=0)
            self.ai_device = self.device.get_ai_device()
            if self.ai_device is None:
                raise RuntimeError("AI device not available")

            ai_config = self.ai_device.get_config()
            info = self.ai_device.get_info()
            for ch in range(info.get_num_chans()):
                try:
                    ai_config.set_chan_type(ch, ul.AiChanType.TC)
                    ai_config.set_chan_tc_type(ch, self.thermocouple_type)
                except Exception:
                    pass

            self.connected = True
            self.simulation_mode = False
            self.last_error = None
            self._last_logged_error = None
            print(f"Connected to device: {chosen}")
            return True

        except Exception as e:
            self.last_error = f"Could not connect to MCC device: {e}"
            self._log_once(self.last_error)
            self.connected = False
            self.simulation_mode = True
            return False

    def disconnect(self):
        try:
            if self.device is not None:
                self.device.disconnect()
                self.device.release()
        except Exception:
            pass
        self.device = None
        self.ai_device = None
        self.connected = False
        self.simulation_mode = True
        self._log_once("Disconnected from MCC device")
        return True

    def _read_hardware_channel(self, ch):
        if self.ai_device is None:
            raise RuntimeError("AI device not available")
        return float(self.ai_device.t_in(ch, self.scale))

    def read_channels(self, channels=None):
        if channels is None:
            channels = [0, 1, 2, 3, 4, 5, 6, 7]
            
        if not self.connected or not self.device:
            self.connect

        if not self.connected or not self.device:
            self.simulation_mode = True
            self.last_error = "Hardware/library unavailable; using simulated data."
            self._log_once(self.last_error)
            return self._simulate(len(channels))

        try:
            readings = []
            failures = 0
            failure_messages = []

            for ch in channels:
                try:
                    readings.append(self._read_hardware_channel(ch))
                except Exception as ch_error:
                    readings.append(None)
                    failures += 1
                    failure_messages.append(f"ch{ch}: {ch_error}")

            if any(v is not None for v in readings):
                self._mark_real_data()
                if failures > 0:
                    self.last_error = f"Partial read failure on {failures} channel(s)."
                    self._log_once(self.last_error)
                return readings

            self.simulation_mode = False
            self.last_error = "All channels returned None."
            self._log_once(self.last_error + " Details: " + " | ".join(failure_messages))
            return readings

        except Exception as e:
            self.last_error = f"Error reading channels: {e}"
            self._log_once(self.last_error)
            if not self.ever_had_real_data:
                self.simulation_mode = True
                return self._simulate(len(channels))
            self.simulation_mode = False
            return [None] * len(channels)

    def read_single_channel(self, channel=0):
        values = self.read_channels([channel])
        return values[0] if values else None

    def read_all_channels(self):
        return self.read_channels(list(range(8)))

    def test_read(self):
        print("\n=== MCC E-TC Hardware Test ===")
        print(f"Device IP: {self.device_ip}")
        print(f"Board Number: {self.board_num}")

        if not self.connect():
            print("Failed to connect to device")
            return False

        print("\nReading all 8 channels...")
        temps = self.read_all_channels()

        for i, value in enumerate(temps):
            print(f"Channel {i}: {value if value is not None else 'N/A'}")

        print("Currently using simulated data" if self.simulation_mode else "Hardware test complete")
        self.disconnect()
        return True


if __name__ == "__main__":
    device = MCCThermocouple(device_ip="192.168.0.101", board_num=0)
    device.test_read()
