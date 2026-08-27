"""
Configuration des URLs principales.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Administration Django
    path("admin/", admin.site.urls),
    # Authentification
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # CRUD données OLTP (admin uniquement)
    path("", include("core.urls")),
    # ETL trigger (admin uniquement)
    path("", include("etl.urls")),
    # Dashboard (page principale)
    path("", include("dashboard.urls")),
    # Mentions légales / Protection des données (LPD)
    path(
        "legal/protection-des-donnees/",
        TemplateView.as_view(template_name="legal/lpd.html"),
        name="lpd",
    ),
]

# Handlers d'erreur personnalisés
handler404 = "core.views.handler404"
handler500 = "core.views.handler500"
