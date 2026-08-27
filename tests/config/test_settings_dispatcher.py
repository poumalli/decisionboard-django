"""Tests — config/settings.py : dispatcher DJANGO_ENV -> settings_dev/settings_prod."""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_settings_dispatcher(monkeypatch, django_env):
    monkeypatch.setenv("DJANGO_ENV", django_env)
    monkeypatch.setenv("SECRET_KEY", "a-real-secret-key-1234567890")
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@localhost/db")
    monkeypatch.setenv("DW_DATABASE_URL", "postgres://u:p@localhost/dw")

    base_spec = importlib.util.spec_from_file_location(
        "config.settings_base", REPO_ROOT / "config" / "settings_base.py"
    )
    base_module = importlib.util.module_from_spec(base_spec)
    monkeypatch.setitem(sys.modules, "config.settings_base", base_module)
    base_spec.loader.exec_module(base_module)

    dispatcher_spec = importlib.util.spec_from_file_location(
        "config.settings", REPO_ROOT / "config" / "settings.py"
    )
    dispatcher_module = importlib.util.module_from_spec(dispatcher_spec)
    dispatcher_spec.loader.exec_module(dispatcher_module)
    return dispatcher_module


class TestSettingsDispatcher:

    def test_production_env_selects_settings_prod(self, monkeypatch):
        module = _load_settings_dispatcher(monkeypatch, "production")
        assert module.DEBUG is False

    def test_default_env_selects_settings_dev(self, monkeypatch):
        module = _load_settings_dispatcher(monkeypatch, "development")
        assert module.DEBUG is True
