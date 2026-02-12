"""
Routes du dashboard — 4 pages + paramètres + export CSV.
"""

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("revenue/", views.revenue, name="revenue"),
    path("consultants/", views.consultants, name="consultants"),
    path("clients/", views.clients, name="clients"),
    path("settings/", views.settings_view, name="settings"),
    path("export/", views.export_csv, name="export_csv"),
]
