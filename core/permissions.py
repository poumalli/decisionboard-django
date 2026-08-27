"""
Décorateurs de contrôle d'accès basés sur les groupes Django.

Groupes disponibles :
  - Administrateur : accès complet (données CRUD + paramètres + ETL)
  - Consultant     : accès lecture seule au dashboard
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """Exige que l'utilisateur appartienne au groupe 'Administrateur' (ou soit superuser)."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="Administrateur").exists()
        ):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return _wrapped


def consultant_required(view_func):
    """Exige que l'utilisateur soit connecté et ait un rôle reconnu (Consultant ou Administrateur)."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if request.user.groups.filter(
            name__in=["Administrateur", "Consultant"]
        ).exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return _wrapped
