"""Regression tests for Dash helper functions and profile callbacks."""

import types

import pytest

from appilcation import app as dash_app


def test_save_recording_to_directory_uses_selected_directory(tmp_path):
    """Selected output folders should receive the exported recording file."""

    target_dir = tmp_path / "user_chosen"
    saved_path = dash_app.save_recording_to_directory("custom_record.txt", "sample-data", output_dir=target_dir)

    assert saved_path == target_dir / "custom_record.txt"
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == "sample-data"


def test_update_interval_from_sampling_clamps_low_values():
    """Sampling intervals should never exceed the minimum 0.1 Hz clamp."""

    assert dash_app.update_interval_from_sampling(5) == 200
    assert dash_app.update_interval_from_sampling(0.05) == int(1000 / 0.1)
    assert dash_app.update_interval_from_sampling(None) == int(1000 / dash_app.DEFAULT_CONFIG["sampling_frequency"])


def test_build_live_cfg_resets_invalid_ranges_and_sampling():
    """Invalid live configuration values should fall back to defaults."""

    cfg = dash_app.build_live_cfg(
        furnace=2,
        setpoint=85,
        lower=70,
        upper=90,
        y_min=95,
        y_max=80,
        sampling=0,
    )

    assert cfg["furnace_number"] == 2
    assert cfg["sampling_frequency"] == dash_app.DEFAULT_CONFIG["sampling_frequency"]
    assert cfg["y_min"] == dash_app.DEFAULT_CONFIG["y_min"]
    assert cfg["y_max"] == dash_app.DEFAULT_CONFIG["y_max"]


def test_build_live_cfg_defaults_non_numeric_furnace():
    """Invalid furnace values should not crash live dashboard updates."""

    cfg = dash_app.build_live_cfg(
        furnace="A",
        setpoint=85,
        lower=70,
        upper=90,
        y_min=50,
        y_max=100,
        sampling=1,
    )

    assert cfg["furnace_number"] == dash_app.DEFAULT_CONFIG["furnace_number"]


def test_make_figure_uses_store_data_and_y_axis_range():
    """The chart should reflect stored data and configured y-axis bounds."""

    store = {"times": ["00:00:01", "00:00:02"], "ch0": [70, 71], "ch1": [71, 72], "ch2": [72, 73]}
    cfg = dash_app.DEFAULT_CONFIG.copy()
    cfg["setpoint"] = 80
    cfg["lower_bound"] = 70
    cfg["upper_bound"] = 90

    fig = dash_app.make_figure(store, cfg)

    assert len(fig.data) == 3
    assert list(fig.data[0].y) == store["ch0"]
    assert list(fig.data[1].y) == store["ch1"]
    assert list(fig.data[2].y) == store["ch2"]
    assert list(fig.layout.yaxis.range) == [cfg["y_min"], cfg["y_max"]]


def test_toggle_save_modal_respects_trigger(monkeypatch):
    """The save modal should respond to Dash's triggering control."""

    monkeypatch.setattr(dash_app, "ctx", types.SimpleNamespace(triggered_id="btn-save-as"))
    assert dash_app.toggle_save_modal(1, 0, 0, False) is True

    monkeypatch.setattr(dash_app, "ctx", types.SimpleNamespace(triggered_id="save-modal-cancel"))
    assert dash_app.toggle_save_modal(0, 1, 0, True) is False
