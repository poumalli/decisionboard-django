"""
Package services du dashboard.

Ré-exporte les fonctions publiques de kpi.py pour maintenir
la rétrocompatibilité : `from . import services` + `services.get_*()`.
"""

from .kpi import (
    get_date_range,
    get_dashboard_summary,
    get_employee_performance,
    get_revenue_summary,
    get_consultants_summary,
    get_clients_summary,
)

__all__ = [
    "get_date_range",
    "get_dashboard_summary",
    "get_employee_performance",
    "get_revenue_summary",
    "get_consultants_summary",
    "get_clients_summary",
]
