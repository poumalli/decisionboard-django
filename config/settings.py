"""
Routeur de configuration — sélectionne l'environnement via DJANGO_ENV.

  DJANGO_ENV=development  →  settings_dev.py   (défaut)
  DJANGO_ENV=production   →  settings_prod.py

Usage production :
  export DJANGO_ENV=production
  export SECRET_KEY=<clé générée>
  export DATABASE_URL=postgresql://...
  gunicorn config.wsgi
"""

import os

_env = os.environ.get("DJANGO_ENV", "development")

if _env == "production":
    from config.settings_prod import *  # noqa: F401, F403
else:
    from config.settings_dev import *  # noqa: F401, F403
