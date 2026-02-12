"""
Vues du dashboard — 4 pages + paramètres + export CSV.
Toutes les vues nécessitent une authentification (@login_required).
"""

import csv
import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from . import services
from .forms import BusinessSettingsForm
from .models import BusinessSettings
from .services.business_metrics import compute_strategic_metrics


# =============================================
# UTILITAIRES
# =============================================


class _ChartEncoder(json.JSONEncoder):
    """Encode Decimal et date/datetime en types JSON natifs pour Chart.js."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def _to_json(data):
    """Convertit des données Python (Decimal, date) en JSON pour les templates."""
    return json.dumps(data, cls=_ChartEncoder)


def _parse_date_filters(request):
    """
    Extrait start_date / end_date depuis les paramètres GET.
    Supporte les presets (month, quarter, year) et les dates manuelles.
    """
    preset = request.GET.get("preset", "")
    today = date.today()

    if preset == "month":
        return today.replace(day=1), today
    if preset == "quarter":
        quarter_start = ((today.month - 1) // 3) * 3 + 1
        return today.replace(month=quarter_start, day=1), today
    if preset == "year":
        return today - timedelta(days=365), today

    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    try:
        start_date = date.fromisoformat(start_str) if start_str else None
        end_date = date.fromisoformat(end_str) if end_str else None
    except ValueError:
        start_date = end_date = None

    if not start_date or not end_date:
        start_date, end_date = services.get_date_range()

    return start_date, end_date


def _get_active_preset(request):
    """Retourne le preset actif pour le highlighting du bouton."""
    return request.GET.get("preset", "")


def _base_context(request, page, start_date, end_date):
    """Contexte commun à toutes les pages du dashboard."""
    return {
        "page": page,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "active_preset": _get_active_preset(request),
    }


def _chart_data(records, label_key, value_key="revenue"):
    """Extrait labels + values depuis une liste de dicts pour Chart.js."""
    labels = [r[label_key] for r in records]
    values = [float(r[value_key]) for r in records]
    return _to_json(labels), _to_json(values)


def _load_settings():
    """Charge la configuration stratégique (singleton)."""
    return BusinessSettings.load()


# =============================================
# PAGE 1 : TABLEAU DE BORD
# =============================================


@login_required
def dashboard(request):
    """Vue principale : KPIs globaux, graphiques, tableau résumé."""
    start_date, end_date = _parse_date_filters(request)
    data = services.get_dashboard_summary(start_date, end_date)
    biz_settings = _load_settings()
    strategic = compute_strategic_metrics(data, biz_settings)

    monthly_labels = _to_json([
        r["month"].strftime("%b %Y") for r in data["monthly_revenue"]
    ])
    monthly_values = _to_json([float(r["revenue"]) for r in data["monthly_revenue"]])
    service_labels, service_values = _chart_data(data["top_services"], "service__name")

    context = {
        **_base_context(request, "dashboard", start_date, end_date),
        "total_revenue": data["total_revenue"],
        "revenue_variation": data["revenue_variation"],
        "total_missions": data["total_missions"],
        "missions_variation": data["missions_variation"],
        "average_basket": data["average_basket"],
        "basket_variation": data["basket_variation"],
        "active_clients": data["active_clients"],
        "clients_variation": data["clients_variation"],
        "utilization_rate": data["utilization_rate"],
        "unpaid": data["unpaid"],
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "top_service_labels": service_labels,
        "top_service_values": service_values,
        "employee_performance": data["employee_performance"],
        "strategic": strategic,
    }
    return render(request, "dashboard/home.html", context)


# =============================================
# PAGE 2 : ANALYSE DES REVENUS
# =============================================


@login_required
def revenue(request):
    """Vue détaillée des revenus : par mois, catégorie, client."""
    start_date, end_date = _parse_date_filters(request)
    category_filter = request.GET.get("category", "")

    data = services.get_revenue_summary(
        start_date, end_date, category=category_filter or None
    )

    monthly_labels = _to_json([
        r["month"].strftime("%b %Y") for r in data["monthly_revenue"]
    ])
    monthly_values = _to_json([float(r["revenue"]) for r in data["monthly_revenue"]])
    category_labels, category_values = _chart_data(data["by_category"], "service__category")

    context = {
        **_base_context(request, "revenue", start_date, end_date),
        "category_filter": category_filter,
        "all_categories": data["categories"],
        "total_revenue": data["total_revenue"],
        "total_missions": data["total_missions"],
        "total_hours": data["total_hours"],
        "revenue_variation": data["revenue_variation"],
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "category_labels": category_labels,
        "category_values": category_values,
        "top_services": data["top_services"],
        "by_client": data["by_client"],
    }
    return render(request, "dashboard/revenue.html", context)


# =============================================
# PAGE 3 : PERFORMANCE CONSULTANTS
# =============================================


@login_required
def consultants(request):
    """Vue détaillée des consultants : CA, heures, taux d'occupation."""
    start_date, end_date = _parse_date_filters(request)
    data = services.get_consultants_summary(start_date, end_date)

    consultant_names = _to_json([c["name"] for c in data["consultants"]])
    consultant_revenues = _to_json([float(c["revenue"]) for c in data["consultants"]])
    consultant_hours = _to_json([c["hours"] for c in data["consultants"]])
    consultant_rates = _to_json([c["utilization_rate"] for c in data["consultants"]])

    context = {
        **_base_context(request, "consultants", start_date, end_date),
        "consultant_count": data["consultant_count"],
        "avg_utilization": data["avg_utilization"],
        "total_hours": data["total_hours"],
        "total_revenue": data["total_revenue"],
        "ca_per_hour": data["ca_per_hour"],
        "consultant_names": consultant_names,
        "consultant_revenues": consultant_revenues,
        "consultant_hours": consultant_hours,
        "consultant_rates": consultant_rates,
        "consultants": data["consultants"],
    }
    return render(request, "dashboard/consultants.html", context)


# =============================================
# PAGE 4 : ANALYSE CLIENTS
# =============================================


@login_required
def clients(request):
    """Vue détaillée des clients : secteurs, ranking, fréquence, inactifs."""
    start_date, end_date = _parse_date_filters(request)
    biz_settings = _load_settings()

    data = services.get_clients_summary(
        start_date,
        end_date,
        inactivity_months=biz_settings.inactivity_months_threshold,
    )

    sector_labels, sector_values = _chart_data(data["by_sector"], "client__sector")

    context = {
        **_base_context(request, "clients", start_date, end_date),
        "total_clients": data["total_clients"],
        "active_clients": data["active_clients"],
        "total_revenue": data["total_revenue"],
        "sector_labels": sector_labels,
        "sector_values": sector_values,
        "ranking": data["ranking"],
        "frequency": data["frequency"],
        "inactive": data["inactive"],
        "inactivity_months": biz_settings.inactivity_months_threshold,
    }
    return render(request, "dashboard/clients.html", context)


# =============================================
# PAGE 5 : PARAMÈTRES STRATÉGIQUES
# =============================================


@login_required
def settings_view(request):
    """Configuration des objectifs stratégiques du cabinet."""
    biz_settings = _load_settings()

    if request.method == "POST":
        form = BusinessSettingsForm(request.POST, instance=biz_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres enregistrés avec succès.")
            return redirect("dashboard:settings")
    else:
        form = BusinessSettingsForm(instance=biz_settings)

    context = {
        "page": "settings",
        "form": form,
    }
    return render(request, "dashboard/settings.html", context)


# =============================================
# EXPORT CSV
# =============================================


@login_required
def export_csv(request):
    """Exporte les performances consultants en CSV."""
    start_date, end_date = _parse_date_filters(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="decisionboard_export_{date.today()}.csv"'
    )

    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Consultant", "Rôle", "CA HT (CHF)", "Missions", "Heures"])

    for row in services.get_employee_performance(start_date, end_date):
        writer.writerow([
            row["employee__full_name"],
            row["employee__role"],
            f'{row["revenue"]:.2f}',
            row["missions"],
            row["hours"],
        ])

    return response
