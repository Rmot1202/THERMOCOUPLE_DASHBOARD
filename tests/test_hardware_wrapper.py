"""Regression tests for the MCC hardware wrapper."""

import builtins
import importlib
import sys
import types

import pytest


def _reload_hardware_with_fake_mcculw(monkeypatch, include_ul=True, t_in_impl=None):
    """Reload the hardware module with a controlled fake MCC package."""

    fake_mcculw = types.ModuleType("mcculw")
    fake_enums = types.SimpleNamespace(TempScale=types.SimpleNamespace(CELSIUS="CELSIUS"))
    fake_mcculw.enums = fake_enums
    fake_mcculw.__path__ = []

    if include_ul:
        class FakeUL:
            """Minimal stand-in for the MCC UL temperature API."""

            def __init__(self, t_in_impl):
                """Store the channel read implementation."""

                self._t_in_impl = t_in_impl

            def t_in(self, board_num, channel, scale):
                """Return or compute a fake thermocouple reading."""

                if callable(self._t_in_impl):
                    return self._t_in_impl(board_num, channel, scale)
                return self._t_in_impl

        fake_ul_module = types.ModuleType("mcculw.ul")
        fake_ul_module.t_in = FakeUL(t_in_impl).t_in
        fake_mcculw.ul = fake_ul_module
        monkeypatch.setitem(sys.modules, "mcculw.ul", fake_ul_module)
    else:
        original_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            """Raise the same import error as a missing MCC UL module."""

            if name == "mcculw" and "ul" in fromlist:
                raise ImportError("No module named 'mcculw.ul'")
            return original_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)

    monkeypatch.setitem(sys.modules, "mcculw", fake_mcculw)
    monkeypatch.setitem(sys.modules, "mcculw.enums", fake_enums)

    if "appilcation.hardware" in sys.modules:
        del sys.modules["appilcation.hardware"]
    import appilcation.hardware as hardware

    return importlib.reload(hardware)


def _reload_hardware_with_fake_uldaq(monkeypatch, descriptor_impl=None):
    """Reload the hardware module with a controlled fake uldaq package."""

    fake_uldaq = types.ModuleType("uldaq")
    fake_uldaq.TempScale = types.SimpleNamespace(CELSIUS="CELSIUS")
    fake_uldaq.TcType = types.SimpleNamespace(R="R")
    fake_uldaq.AiChanType = types.SimpleNamespace(TC="TC")
    fake_uldaq.ULException = RuntimeError

    def get_net_daq_device_descriptor(*args, **kwargs):
        if descriptor_impl:
            return descriptor_impl(*args, **kwargs)
        raise AssertionError("uldaq descriptor lookup should not be called")

    fake_uldaq.get_net_daq_device_descriptor = get_net_daq_device_descriptor
    monkeypatch.setitem(sys.modules, "uldaq", fake_uldaq)

    if "appilcation.hardware" in sys.modules:
        del sys.modules["appilcation.hardware"]
    import appilcation.hardware as hardware

    return importlib.reload(hardware)


def test_connect_reports_failure_when_library_missing(monkeypatch):
    """A missing MCC library should report that hardware is unavailable."""

    hardware = _reload_hardware_with_fake_mcculw(monkeypatch, include_ul=False)

    device = hardware.MCCThermocouple(device_ip="192.168.1.100")

    assert device.ul is None
    assert device.connect() is False
    assert device.connected is False
    assert "not available" in device.last_error.lower()


def test_connect_succeeds_with_fake_mcculw(monkeypatch):
    """A fake MCC library should allow a successful connection."""

    hardware = _reload_hardware_with_fake_mcculw(monkeypatch, include_ul=True, t_in_impl=20.0)

    device = hardware.MCCThermocouple(device_ip="192.168.1.101")
    assert device.connect() is True
    assert device.connected is True
    assert device.last_error is None


def test_read_channels_returns_real_values_and_accepts_negative(monkeypatch):
    """Hardware reads should preserve real channel values, including negatives."""

    def fake_t_in(board, channel, scale):
        """Return deterministic fake temperatures per channel."""

        return -10.5 if channel == 0 else float(channel * 2)

    hardware = _reload_hardware_with_fake_mcculw(monkeypatch, include_ul=True, t_in_impl=fake_t_in)
    device = hardware.MCCThermocouple()
    device.connect()

    temperatures = device.read_channels([0, 1, 2])

    assert temperatures == [-10.5, 2.0, 4.0]
    assert device.last_error is None


def test_read_channels_returns_none_on_all_errors(monkeypatch):
    """All channel read failures should return blanks instead of fake data."""

    def failing_t_in(board, channel, scale):
        """Raise a hardware-like error for every channel read."""

        raise RuntimeError(f"hardware failure on channel {channel}")

    hardware = _reload_hardware_with_fake_mcculw(monkeypatch, include_ul=True, t_in_impl=failing_t_in)
    device = hardware.MCCThermocouple()
    device.connect()

    temps = device.read_channels([0, 1, 2])

    assert temps == [None, None, None]
    assert "all hardware channel reads failed" in device.last_error.lower()


def test_disconnect_clears_connection(monkeypatch):
    """Disconnecting should clear the connection."""

    hardware = _reload_hardware_with_fake_mcculw(monkeypatch, include_ul=True, t_in_impl=20.0)
    device = hardware.MCCThermocouple()
    device.connect()

    assert device.disconnect() is True
    assert device.connected is False


def test_connect_fails_fast_when_network_device_is_unreachable(monkeypatch):
    """An offline DAQ should not let the uldaq descriptor lookup block startup."""

    hardware = _reload_hardware_with_fake_uldaq(monkeypatch)

    def fake_create_connection(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(hardware.socket, "create_connection", fake_create_connection)

    device = hardware.MCCThermocouple(
        device_ip="169.254.69.179",
        connection_timeout=0.01,
        reconnect_interval=5.0,
    )

    assert device.connect() is False
    assert device.connected is False
    assert "not reachable" in device.last_error.lower()
