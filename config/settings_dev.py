"""
Settings développement — DEBUG activé, SQLite local, logs console.
"""

from config.settings_base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", "0.0.0.0"]

# Emails dans la console en dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Barre de débogage Django (optionnel, décommentez si installé)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]
