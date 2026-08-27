"""
Settings production — Sécurité renforcée, PostgreSQL, logging fichier.

Variables d'environnement obligatoires :
  SECRET_KEY          Clé secrète Django (min. 50 caractères aléatoires)
  DATABASE_URL        URL PostgreSQL OLTP (ex: postgresql://user:pass@host/db)
  DW_DATABASE_URL     URL PostgreSQL DW
  ALLOWED_HOSTS       Domaine(s) autorisés séparés par virgule

Variables optionnelles :
  ADMIN_EMAIL         Email pour recevoir les erreurs 500
  EMAIL_HOST          Serveur SMTP (défaut: localhost)
  EMAIL_PORT          Port SMTP (défaut: 587)
  EMAIL_HOST_USER     Identifiant SMTP
  EMAIL_HOST_PASSWORD Mot de passe SMTP
  SENTRY_DSN          URL Sentry pour le monitoring des erreurs
"""

import os
import logging.handlers  # noqa: F401 — requis pour RotatingFileHandler

from config.settings_base import *  # noqa: F401, F403

# --- Sécurité ---
DEBUG = False

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()
]

# Validation stricte : empêche le démarrage avec la clé par défaut
if SECRET_KEY == "django-insecure-dev-key-change-in-prod":
    raise ValueError(
        "SECRET_KEY doit être remplacée en production. "
        'Générez-en une avec : python -c "import secrets; print(secrets.token_urlsafe(50))"'
    )

# Fichiers statiques avec manifest (cache-busting) — nécessite `collectstatic`
# avant le déploiement.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Headers de sécurité HTTP
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# HTTPS — activer UNIQUEMENT après avoir configuré un certificat SSL valide
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000   # 1 an — irréversible pendant cette durée
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# --- Email (erreurs serveur) ---
ADMINS = [("Administrateur", os.environ.get("ADMIN_EMAIL", ""))]
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "noreply@decisionboard.ch")
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# --- Logging vers fichier rotatif ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} — {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "decisionboard.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": False,
        },
        "etl": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# --- Sentry (optionnel) ---
_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=_sentry_dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
    except ImportError:
        pass  # sentry-sdk non installé, on ignore
