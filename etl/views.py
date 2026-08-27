"""
Vue ETL — déclenche le pipeline depuis l'interface admin.
Accès réservé aux administrateurs.
"""

from django.contrib import messages
from django.core.management import call_command
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from core.permissions import admin_required


@admin_required
def run_etl_view(request):
    """Lance le pipeline ETL via POST uniquement."""
    if request.method != "POST":
        return redirect("dashboard:home")

    try:
        call_command("run_etl")
        messages.success(request, "Pipeline ETL exécuté avec succès.")
    except Exception as exc:
        messages.error(request, f"Erreur ETL : {exc}")

    next_url = request.POST.get("next", "/")
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = "/"
    return redirect(next_url)
