"""
Configuration de l'interface d'administration Django.
Permet de gérer les données OLTP via /admin/.
"""

from django.contrib import admin
from .models import Client, Employee, Service, Appointment, Invoice, Payment


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_name", "sector", "city", "created_at")
    list_filter = ("sector", "city")
    search_fields = ("company_name", "contact_name", "email")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "role", "hourly_rate", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "duration_hours")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("service", "client", "employee", "date", "status", "duration_hours")
    list_filter = ("status", "date", "employee")
    search_fields = ("client__company_name", "employee__last_name")
    date_hierarchy = "date"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "appointment",
        "amount_ht",
        "amount_ttc",
        "status",
        "issued_date",
    )
    list_filter = ("status", "issued_date")
    search_fields = ("invoice_number",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "payment_date", "method")
    list_filter = ("method", "payment_date")
