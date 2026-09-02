import socket
import time

try:
    import uldaq as ul
    _LEGACY_UL = False
except Exception as uldaq_error:
    try:
        from mcculw import ul
        _LEGACY_UL = True
    except Exception:
        ul = None
        _LEGACY_UL = False
        print(f"Neither uldaq nor mcculw.ul could be imported: {uldaq_error}")
_UL_EXCEPTION = getattr(ul, "ULException", type("_ULException", (Exception,), {}))


class MCCThermocouple:
    def __init__(
        self,
        device_ip="169.254.69.179",
        board_num=0,
        interface_name="eth0",
        port=54211,
        connection_timeout=1.0,
        reconnect_interval=5.0,
    ):
        self.device_ip = device_ip
        self.board_num = board_num
        self.interface_name = interface_name
        self.port = port
        self.connection_timeout = float(connection_timeout)
        self.reconnect_interval = float(reconnect_interval)
        self.ul = ul

        self.connected = False
        self.device = None
        self.ai_device = None
        self.last_error = None
        self._last_logged_error = None
        self._last_connect_attempt_ts = None
        self.ever_had_real_data = False
        self.last_real_data_ts = None
        self.thermocouple_type_name = "R"

        self.scale = getattr(getattr(ul, "TempScale", None), "CELSIUS", None) if ul else None
        self.thermocouple_type = getattr(getattr(ul, "TcType", None), "R", None) if ul else None

        if ul is None:
            self.last_error = "uldaq library unavailable"
            self._log_once(self.last_error)
        elif _LEGACY_UL:
            self.connected = True

    def _log_once(self, message):
        if message != self._last_logged_error:
            print(message)
            self._last_logged_error = message

    def _mark_real_data(self):
        self.ever_had_real_data = True
        self.last_real_data_ts = time.time()

    def _connect_retry_due(self):
        if self._last_connect_attempt_ts is None:
            return True
        return (time.time() - self._last_connect_attempt_ts) >= self.reconnect_interval

    def _network_device_reachable(self):
        if not self.device_ip:
            return True

        try:
            with socket.create_connection((self.device_ip, self.port), timeout=self.connection_timeout):
                return True
        except OSError as error:
            self.last_error = f"DAQ is not reachable at {self.device_ip}:{self.port}: {error}"
            self._log_once(self.last_error)
            return False

    def connect(self):
        if ul is None:
            self.connected = False
            self.last_error = "uldaq library not available."
            self._log_once(self.last_error)
            return False

        if _LEGACY_UL:
            self.connected = True
            self.last_error = None
            return True

        if self.connected and self.device is not None and self.ai_device is not None:
            return True

        if not self._connect_retry_due():
            return False

        self._last_connect_attempt_ts = time.time()

        try:
            if not self._network_device_reachable():
                return False

            desc = ul.get_net_daq_device_descriptor(
                self.device_ip,
                self.port,
                self.interface_name
            )

            self.device = ul.DaqDevice(desc)
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
                except Exception as e:
                    self._log_once(f"Channel {ch} config warning: {e}")

            self.connected = True
            self.last_error = None
            self._last_logged_error = None
            self._last_connect_attempt_ts = None
            print(f"Connected to device: {desc}")
            return True

        except Exception as e:
            self.last_error = f"Could not connect to MCC device: {e}"
            self._log_once(self.last_error)
            self.connected = False
            try:
                if self.device is not None:
                    self.device.release()
            except Exception:
                pass
            self.device = None
            self.ai_device = None
            return False

    def disconnect(self):
        try:
            if self.device is not None and self.device.is_connected():
                self.device.disconnect()
            if self.device is not None:
                self.device.release()
        except Exception:
            pass

        self.device = None
        self.ai_device = None
        self.connected = False
        self._log_once("Disconnected from MCC device")
        return True

    def set_thermocouple_type(self, type_name):
        """Apply a thermocouple type to every configured analog channel."""

        type_name = str(type_name or "R").upper()
        tc_types = getattr(self.ul, "TcType", None) if self.ul else None
        selected_type = getattr(tc_types, type_name, None) if tc_types else None
        if selected_type is None:
            type_name = "R"
            selected_type = getattr(tc_types, type_name, self.thermocouple_type)

        self.thermocouple_type_name = type_name
        self.thermocouple_type = selected_type
        if not self.connected or self.ai_device is None or _LEGACY_UL:
            return False

        try:
            ai_config = self.ai_device.get_config()
            info = self.ai_device.get_info()
            for channel in range(info.get_num_chans()):
                ai_config.set_chan_tc_type(channel, selected_type)
            return True
        except Exception as error:
            self.last_error = f"Could not set thermocouple type: {error}"
            self._log_once(self.last_error)
            return False

    def _read_hardware_channel(self, ch):
        if _LEGACY_UL:
            return float(ul.t_in(self.board_num, ch, self.scale))
        if self.ai_device is None:
            raise RuntimeError("AI device not available")
        return float(self.ai_device.t_in(ch, self.scale))

    def read_channels(self, channels=None):
        if channels is None:
            channels = [0, 1, 2, 3, 4, 5, 6, 7]

        if not self.connected or (not _LEGACY_UL and (self.device is None or self.ai_device is None)):
            self.connect()

        if not self.connected or (not _LEGACY_UL and (self.device is None or self.ai_device is None)):
            self.last_error = "DAQ is not connected."
            self._log_once(self.last_error)
            return [None] * len(channels)

        try:
            readings = []
            failures = 0
            failure_messages = []

            for ch in channels:
                try:
                    readings.append(self._read_hardware_channel(ch))
                except _UL_EXCEPTION as ch_error:
                    if ch_error.error_code == ul.ULError.OPEN_CONNECTION:
                        readings.append(None)
                        failures += 1
                        failure_messages.append(f"ch{ch}: Open Connection")
                    else:
                        readings.append(None)
                        failures += 1
                        failure_messages.append(f"ch{ch}: {ch_error}")
                except Exception as ch_error:
                    readings.append(None)
                    failures += 1
                    failure_messages.append(f"ch{ch}: {ch_error}")

            if any(v is not None for v in readings):
                self._mark_real_data()
                if failures > 0:
                    self.last_error = f"Partial read failure on {failures} channel(s)."
                    self._log_once(self.last_error + " " + " | ".join(failure_messages))
                else:
                    self.last_error = None
                return readings

            self.last_error = "All hardware channel reads failed."
            self._log_once(self.last_error + " Details: " + " | ".join(failure_messages))
            return [None] * len(channels)

        except Exception as e:
            self.last_error = f"Error reading channels: {e}"
            self._log_once(self.last_error)
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
        print(f"Interface: {self.interface_name}")
        print(f"Port: {self.port}")

        if not self.connect():
            print("Failed to connect to device")
            return False

        print("\nReading all 8 channels...")
        temps = self.read_all_channels()

        for i, value in enumerate(temps):
            print(f"Channel {i}: {value if value is not None else 'Open/Unavailable'}")

        print("Hardware test complete")
        self.disconnect()
        return True


if __name__ == "__main__":
    device = MCCThermocouple(
        device_ip="169.254.69.179",
        board_num=0,
        interface_name="eth0",
        port=54211
    )
    device.test_read()
