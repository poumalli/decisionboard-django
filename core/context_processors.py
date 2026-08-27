"""Context processors — variables disponibles dans tous les templates."""

from django.conf import settings


def user_role(request):
    """Injecte user_is_admin dans le contexte de tous les templates."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"user_is_admin": False}
    return {
        "user_is_admin": (
            user.is_superuser or user.groups.filter(name="Administrateur").exists()
        ),
    }


def etl_status(request):
    """Injecte la date/heure de la dernière exécution ETL."""
    filepath = settings.BASE_DIR / ".etl_last_run"
    if filepath.exists():
        return {"etl_last_run": filepath.read_text().strip()}
    return {"etl_last_run": None}
