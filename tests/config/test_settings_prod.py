"""Tests — config/settings_prod.py

settings_prod.py n'est jamais importé pendant la suite normale (les tests
tournent avec DJANGO_ENV non défini -> settings_dev). On le charge ici
directement via importlib, avec un config/settings_base.py frais injecté
dans sys.modules pour que la variable SECRET_KEY reflète bien l'environnement
de chaque test plutôt que la valeur mise en cache au démarrage de pytest.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_prod_settings(monkeypatch, secret_key, **extra_env):
    monkeypatch.setenv("SECRET_KEY", secret_key)
    monkeypatch.setenv("ALLOWED_HOSTS", extra_env.pop("ALLOWED_HOSTS", "example.com"))
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@localhost/db")
    monkeypatch.setenv("DW_DATABASE_URL", "postgres://u:p@localhost/dw")
    for key, value in extra_env.items():
        monkeypatch.setenv(key, value)

    base_spec = importlib.util.spec_from_file_location(
        "config.settings_base", REPO_ROOT / "config" / "settings_base.py"
    )
    base_module = importlib.util.module_from_spec(base_spec)
    monkeypatch.setitem(sys.modules, "config.settings_base", base_module)
    base_spec.loader.exec_module(base_module)

    prod_spec = importlib.util.spec_from_file_location(
        "config.settings_prod", REPO_ROOT / "config" / "settings_prod.py"
    )
    prod_module = importlib.util.module_from_spec(prod_spec)
    prod_spec.loader.exec_module(prod_module)
    return prod_module


class TestSettingsProd:

    def test_raises_with_default_insecure_key(self, monkeypatch):
        with pytest.raises(ValueError, match="SECRET_KEY doit être remplacée"):
            _load_prod_settings(monkeypatch, "django-insecure-dev-key-change-in-prod")

    def test_loads_with_real_secret_key(self, monkeypatch):
        module = _load_prod_settings(monkeypatch, "a-real-secret-key-1234567890")
        assert module.DEBUG is False
        assert module.ALLOWED_HOSTS == ["example.com"]
        assert (
            module.STATICFILES_STORAGE
            == "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )

    def test_allowed_hosts_parses_multiple_comma_separated_domains(self, monkeypatch):
        module = _load_prod_settings(
            monkeypatch,
            "a-real-secret-key-1234567890",
            ALLOWED_HOSTS="one.example.com, two.example.com",
        )
        assert module.ALLOWED_HOSTS == ["one.example.com", "two.example.com"]

    def test_sentry_dsn_set_but_package_missing_is_ignored(self, monkeypatch):
        """sentry-sdk n'est pas installé dans cet environnement : la branche
        ImportError doit être avalée silencieusement plutôt que de faire
        planter le chargement des settings."""
        module = _load_prod_settings(
            monkeypatch,
            "a-real-secret-key-1234567890",
            SENTRY_DSN="https://fakekey@sentry.example.com/1",
        )
        assert module.DEBUG is False

    def test_sentry_dsn_set_and_package_available_initializes_it(self, monkeypatch):
        """Avec sentry_sdk disponible, sentry_sdk.init() doit être appelé
        avec le DSN fourni — simulé ici via un faux module en l'absence du
        vrai package dans cet environnement."""
        import types

        init_calls = []
        fake_sentry_sdk = types.ModuleType("sentry_sdk")
        fake_sentry_sdk.init = lambda **kwargs: init_calls.append(kwargs)
        fake_integrations_pkg = types.ModuleType("sentry_sdk.integrations")
        fake_integrations_django = types.ModuleType("sentry_sdk.integrations.django")
        fake_integrations_django.DjangoIntegration = object
        fake_integrations_pkg.django = fake_integrations_django
        fake_sentry_sdk.integrations = fake_integrations_pkg
        monkeypatch.setitem(sys.modules, "sentry_sdk", fake_sentry_sdk)
        monkeypatch.setitem(
            sys.modules, "sentry_sdk.integrations", fake_integrations_pkg
        )
        monkeypatch.setitem(
            sys.modules, "sentry_sdk.integrations.django", fake_integrations_django
        )

        _load_prod_settings(
            monkeypatch,
            "a-real-secret-key-1234567890",
            SENTRY_DSN="https://fakekey@sentry.example.com/1",
        )

        assert len(init_calls) == 1
        assert init_calls[0]["dsn"] == "https://fakekey@sentry.example.com/1"
