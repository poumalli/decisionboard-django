"""
Services KPI — Calcul des indicateurs clés de performance.

Toutes les requêtes lisent depuis le Data Warehouse (base 'dw').
Chaque fonction accepte un filtre de dates (start_date, end_date).

Organisation :
  - Utilitaires (dates, variation, queryset de base)
  - Dashboard principal
  - Analyse des revenus
  - Performance consultants
  - Analyse clients
"""

from datetime import date, timedelta

from django.db.models import Avg, Count, Max, Sum
from django.db.models.functions import TruncMonth

from dw.models import DimClient, DimService, FactSales


# =============================================
# UTILITAIRES
# =============================================


def get_date_range(months_back=12):
    """Plage de dates par défaut : les N derniers mois."""
    end = date.today()
    start = end - timedelta(days=months_back * 30)
    return start, end


def _get_previous_period(start_date, end_date):
    """Période précédente de même durée (pour comparaisons N vs N-1)."""
    duration = (end_date - start_date).days
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=duration)
    return prev_start, prev_end


def _compute_variation(current, previous):
    """Pourcentage de variation entre deux valeurs."""
    current = float(current or 0)
    previous = float(previous or 0)
    if previous > 0:
        return round(((current - previous) / previous) * 100, 1)
    return 100.0 if current > 0 else 0.0


def _base_qs(start_date, end_date):
    """QuerySet de base filtré par période sur FactSales."""
    return (
        FactSales.objects.using("dw")
        .filter(date__full_date__gte=start_date, date__full_date__lte=end_date)
    )


# =============================================
# DASHBOARD PRINCIPAL
# =============================================


def get_dashboard_summary(start_date, end_date):
    """Toutes les données du dashboard en un seul appel."""
    prev_start, prev_end = _get_previous_period(start_date, end_date)

    current_qs = _base_qs(start_date, end_date)
    prev_qs = _base_qs(prev_start, prev_end)

    # Période courante — agrégats en une seule requête
    current_agg = current_qs.aggregate(
        total=Sum("total_ht"),
        avg=Avg("total_ht"),
        count=Count("id"),
    )
    active_clients = current_qs.values("client").distinct().count()

    # Période précédente — agrégats en une seule requête
    prev_agg = prev_qs.aggregate(
        total=Sum("total_ht"),
        avg=Avg("total_ht"),
        count=Count("id"),
    )
    prev_clients = prev_qs.values("client").distinct().count()

    return {
        "total_revenue": current_agg["total"] or 0,
        "revenue_variation": _compute_variation(current_agg["total"], prev_agg["total"]),
        "total_missions": current_agg["count"],
        "missions_variation": _compute_variation(current_agg["count"], prev_agg["count"]),
        "average_basket": current_agg["avg"] or 0,
        "basket_variation": _compute_variation(current_agg["avg"], prev_agg["avg"]),
        "active_clients": active_clients,
        "clients_variation": _compute_variation(active_clients, prev_clients),
        "utilization_rate": _get_utilization_rate(start_date, end_date),
        "unpaid": _get_unpaid_amount(start_date, end_date),
        "monthly_revenue": _get_monthly_revenue(start_date, end_date),
        "top_services": _get_top_services(start_date, end_date),
        "employee_performance": get_employee_performance(start_date, end_date),
    }


def _get_monthly_revenue(start_date, end_date):
    """CA HT par mois (graphique d'évolution)."""
    return list(
        _base_qs(start_date, end_date)
        .annotate(month=TruncMonth("date__full_date"))
        .values("month")
        .annotate(revenue=Sum("total_ht"))
        .order_by("month")
    )


def _get_top_services(start_date, end_date, limit=5):
    """Top N services par CA HT."""
    return list(
        _base_qs(start_date, end_date)
        .values("service__name", "service__category")
        .annotate(revenue=Sum("total_ht"), count=Count("id"))
        .order_by("-revenue")[:limit]
    )


def get_employee_performance(start_date, end_date):
    """CA HT, missions et heures par consultant."""
    return list(
        _base_qs(start_date, end_date)
        .values("employee__full_name", "employee__role")
        .annotate(
            revenue=Sum("total_ht"),
            missions=Count("id"),
            hours=Sum("duration_hours"),
        )
        .order_by("-revenue")
    )


def _get_utilization_rate(start_date, end_date):
    """Taux d'occupation : heures facturées / heures ouvrables."""
    nb_days = (end_date - start_date).days
    workable_hours = max(1, int(nb_days * 0.7) * 8)

    results = (
        _base_qs(start_date, end_date)
        .values("employee__full_name")
        .annotate(billed_hours=Sum("duration_hours"))
    )

    rates = []
    for r in results:
        rate = r["billed_hours"] / workable_hours * 100 if workable_hours else 0
        rates.append({
            "employee": r["employee__full_name"],
            "billed_hours": r["billed_hours"],
            "workable_hours": workable_hours,
            "rate": round(rate, 1),
        })

    avg_rate = sum(r["rate"] for r in rates) / len(rates) if rates else 0
    return {"details": rates, "average": round(avg_rate, 1)}


def _get_unpaid_amount(start_date, end_date):
    """Montant HT des missions non payées."""
    result = (
        _base_qs(start_date, end_date)
        .filter(is_paid=False)
        .aggregate(total=Sum("total_ht"), count=Count("id"))
    )
    return {"amount": result["total"] or 0, "count": result["count"] or 0}


# =============================================
# ANALYSE DES REVENUS
# =============================================


def get_revenue_summary(start_date, end_date, category=None):
    """Données complètes pour la page Analyse des revenus."""
    qs = _base_qs(start_date, end_date)
    if category:
        qs = qs.filter(service__category=category)

    totals = qs.aggregate(
        total=Sum("total_ht"),
        count=Count("id"),
        hours=Sum("duration_hours"),
    )

    # Comparaison N-1
    prev_start, prev_end = _get_previous_period(start_date, end_date)
    prev_qs = _base_qs(prev_start, prev_end)
    if category:
        prev_qs = prev_qs.filter(service__category=category)
    prev_revenue = prev_qs.aggregate(total=Sum("total_ht"))["total"] or 0

    # Catégories disponibles (pour le filtre)
    categories = list(
        DimService.objects.using("dw")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    # CA par catégorie (doughnut)
    by_category = list(
        _base_qs(start_date, end_date)
        .values("service__category")
        .annotate(revenue=Sum("total_ht"), count=Count("id"))
        .order_by("-revenue")
    )

    # CA par client (tableau)
    by_client = list(
        _base_qs(start_date, end_date)
        .values("client__company_name", "client__sector")
        .annotate(
            revenue=Sum("total_ht"),
            missions=Count("id"),
            avg_mission=Avg("total_ht"),
        )
        .order_by("-revenue")
    )

    return {
        "total_revenue": totals["total"] or 0,
        "total_missions": totals["count"] or 0,
        "total_hours": totals["hours"] or 0,
        "revenue_variation": _compute_variation(totals["total"] or 0, prev_revenue),
        "monthly_revenue": _get_monthly_revenue(start_date, end_date),
        "by_category": by_category,
        "by_client": by_client,
        "top_services": _get_top_services(start_date, end_date, limit=6),
        "categories": categories,
        "selected_category": category or "",
    }


# =============================================
# PERFORMANCE CONSULTANTS
# =============================================


def get_consultants_summary(start_date, end_date):
    """Données complètes pour la page Performance consultants."""
    nb_days = (end_date - start_date).days
    workable_hours = max(1, int(nb_days * 0.7) * 8)

    results = list(
        _base_qs(start_date, end_date)
        .values("employee__full_name", "employee__role", "employee__seniority_years")
        .annotate(
            revenue=Sum("total_ht"),
            missions=Count("id"),
            hours=Sum("duration_hours"),
            avg_per_mission=Avg("total_ht"),
        )
        .order_by("-revenue")
    )

    consultants = []
    for r in results:
        rate = r["hours"] / workable_hours * 100 if workable_hours else 0
        revenue_float = float(r["revenue"])
        consultants.append({
            "name": r["employee__full_name"],
            "role": r["employee__role"],
            "seniority": r["employee__seniority_years"],
            "revenue": r["revenue"],
            "missions": r["missions"],
            "hours": r["hours"],
            "avg_per_mission": r["avg_per_mission"],
            "utilization_rate": round(rate, 1),
            "workable_hours": workable_hours,
            "ca_per_hour": round(revenue_float / r["hours"], 2) if r["hours"] else 0,
        })

    total_hours = sum(c["hours"] for c in consultants) if consultants else 0
    total_revenue = sum(float(c["revenue"]) for c in consultants) if consultants else 0
    avg_rate = sum(c["utilization_rate"] for c in consultants) / len(consultants) if consultants else 0

    return {
        "consultants": consultants,
        "avg_utilization": round(avg_rate, 1),
        "total_hours": total_hours,
        "total_revenue": total_revenue,
        "consultant_count": len(consultants),
        "ca_per_hour": round(total_revenue / total_hours, 2) if total_hours else 0,
    }


# =============================================
# ANALYSE CLIENTS
# =============================================


def get_clients_summary(start_date, end_date, inactivity_months=3):
    """Données complètes pour la page Analyse clients."""

    # Classement clients par CA
    ranking = list(
        _base_qs(start_date, end_date)
        .values("client__company_name", "client__sector", "client__city")
        .annotate(
            revenue=Sum("total_ht"),
            missions=Count("id"),
            avg_mission=Avg("total_ht"),
            hours=Sum("duration_hours"),
        )
        .order_by("-revenue")
    )

    total_revenue = sum(float(r["revenue"]) for r in ranking) if ranking else 0

    # Pourcentage du CA par client
    for r in ranking:
        r["pct_revenue"] = round(float(r["revenue"]) / total_revenue * 100, 1) if total_revenue else 0

    # Clients actifs
    active_clients = (
        _base_qs(start_date, end_date)
        .values("client").distinct().count()
    )

    # CA par secteur (doughnut)
    by_sector = list(
        _base_qs(start_date, end_date)
        .values("client__sector")
        .annotate(revenue=Sum("total_ht"), client_count=Count("client", distinct=True))
        .order_by("-revenue")
    )

    # Fréquence des missions par client
    frequency = list(
        _base_qs(start_date, end_date)
        .values("client__company_name")
        .annotate(
            total_missions=Count("id"),
            active_months=Count("date__month", distinct=True),
        )
        .order_by("-active_months")
    )

    # Clients inactifs (sans N+1, seuil paramétrable)
    inactive = _get_inactive_clients(inactivity_months)

    return {
        "total_clients": len(ranking),
        "total_revenue": total_revenue,
        "active_clients": active_clients,
        "by_sector": by_sector,
        "ranking": ranking,
        "frequency": frequency,
        "inactive": inactive,
    }


def _get_inactive_clients(inactivity_months=3):
    """Clients sans mission depuis N mois — optimisé sans N+1."""
    threshold_date = date.today() - timedelta(days=inactivity_months * 30)

    all_clients = set(
        DimClient.objects.using("dw").values_list("company_name", flat=True)
    )

    active_clients = set(
        FactSales.objects.using("dw")
        .filter(date__full_date__gte=threshold_date)
        .values_list("client__company_name", flat=True)
        .distinct()
    )

    inactive_names = all_clients - active_clients
    if not inactive_names:
        return []

    # Dernière mission de chaque client inactif — UNE seule requête
    last_missions = dict(
        FactSales.objects.using("dw")
        .filter(client__company_name__in=inactive_names)
        .values("client__company_name")
        .annotate(last_date=Max("date__full_date"))
        .values_list("client__company_name", "last_date")
    )

    return [
        {"name": name, "last_mission": last_missions.get(name)}
        for name in sorted(inactive_names)
    ]
