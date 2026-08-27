"""
Service de métriques stratégiques.

Compare les KPIs réels aux objectifs définis dans BusinessSettings.
Fournit des statuts (success / warning / danger) pour chaque indicateur.

Aucune requête ORM ici — reçoit les données déjà calculées par kpi.py.
"""


def _status_from_pct(achievement_pct, good=90, acceptable=70):
    """Détermine le statut à partir d'un pourcentage d'atteinte."""
    if achievement_pct >= good:
        return "success"
    if achievement_pct >= acceptable:
        return "warning"
    return "danger"


def compute_strategic_metrics(dashboard_data, settings):
    """
    Compare les données du dashboard aux objectifs stratégiques.

    Paramètres :
        dashboard_data : dict retourné par get_dashboard_summary()
        settings : instance de BusinessSettings (ou None)

    Retourne un dict de métriques comparatives, ou {} si pas de settings.
    """
    if not settings:
        return {}

    metrics = {}

    # --- CA vs objectif mensuel ---
    total_revenue = float(dashboard_data.get("total_revenue", 0))
    monthly_target = float(settings.monthly_revenue_target)

    if monthly_target > 0:
        monthly_data = dashboard_data.get("monthly_revenue", [])
        nb_months = max(len(monthly_data), 1)
        period_target = monthly_target * nb_months
        achievement_pct = (total_revenue / period_target) * 100

        metrics["revenue"] = {
            "monthly_target": monthly_target,
            "period_target": period_target,
            "achievement_pct": round(achievement_pct, 1),
            "gap": round(total_revenue - period_target, 2),
            "status": _status_from_pct(achievement_pct),
        }

    # --- Taux d'occupation vs objectif ---
    utilization = dashboard_data.get("utilization_rate", {})
    avg_rate = (
        float(utilization.get("average", 0)) if isinstance(utilization, dict) else 0
    )
    target_rate = settings.occupation_rate_target

    if target_rate > 0:
        occ_pct = (avg_rate / target_rate) * 100
        metrics["occupation"] = {
            "target": target_rate,
            "actual": avg_rate,
            "achievement_pct": round(occ_pct, 1),
            "status": _status_from_pct(occ_pct),
        }

    # --- Panier moyen vs objectif ---
    avg_basket = float(dashboard_data.get("average_basket", 0))
    basket_target = float(settings.average_basket_target)

    if basket_target > 0:
        basket_pct = (avg_basket / basket_target) * 100
        metrics["basket"] = {
            "target": basket_target,
            "actual": avg_basket,
            "achievement_pct": round(basket_pct, 1),
            "gap": round(avg_basket - basket_target, 2),
            "status": _status_from_pct(basket_pct),
        }

    # --- Créances vs seuil d'alerte ---
    unpaid = dashboard_data.get("unpaid", {})
    unpaid_amount = float(unpaid.get("amount", 0)) if isinstance(unpaid, dict) else 0
    receivables_threshold = float(settings.receivables_alert_threshold)

    metrics["receivables"] = {
        "threshold": receivables_threshold,
        "amount": unpaid_amount,
        "is_alert": unpaid_amount >= receivables_threshold,
        "status": "danger" if unpaid_amount >= receivables_threshold else "success",
    }

    return metrics
