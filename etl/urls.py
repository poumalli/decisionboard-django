from django.urls import path

from . import views

app_name = "etl"

urlpatterns = [
    path("etl/run/", views.run_etl_view, name="run_etl"),
]
