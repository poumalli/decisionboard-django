"""
Routes CRUD pour les entités OLTP (accès administrateur uniquement).
"""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Clients
    path("data/clients/", views.ClientListView.as_view(), name="client_list"),
    path("data/clients/new/", views.ClientCreateView.as_view(), name="client_create"),
    path(
        "data/clients/<int:pk>/",
        views.ClientDetailView.as_view(),
        name="client_detail",
    ),
    path(
        "data/clients/<int:pk>/edit/",
        views.ClientUpdateView.as_view(),
        name="client_update",
    ),
    path(
        "data/clients/<int:pk>/delete/",
        views.ClientDeleteView.as_view(),
        name="client_delete",
    ),
    # Consultants
    path("data/employees/", views.EmployeeListView.as_view(), name="employee_list"),
    path(
        "data/employees/new/",
        views.EmployeeCreateView.as_view(),
        name="employee_create",
    ),
    path(
        "data/employees/<int:pk>/",
        views.EmployeeDetailView.as_view(),
        name="employee_detail",
    ),
    path(
        "data/employees/<int:pk>/edit/",
        views.EmployeeUpdateView.as_view(),
        name="employee_update",
    ),
    path(
        "data/employees/<int:pk>/delete/",
        views.EmployeeDeleteView.as_view(),
        name="employee_delete",
    ),
    # Services
    path("data/services/", views.ServiceListView.as_view(), name="service_list"),
    path(
        "data/services/new/", views.ServiceCreateView.as_view(), name="service_create"
    ),
    path(
        "data/services/<int:pk>/edit/",
        views.ServiceUpdateView.as_view(),
        name="service_update",
    ),
    path(
        "data/services/<int:pk>/delete/",
        views.ServiceDeleteView.as_view(),
        name="service_delete",
    ),
    # Missions
    path(
        "data/appointments/",
        views.AppointmentListView.as_view(),
        name="appointment_list",
    ),
    path(
        "data/appointments/new/",
        views.AppointmentCreateView.as_view(),
        name="appointment_create",
    ),
    path(
        "data/appointments/<int:pk>/edit/",
        views.AppointmentUpdateView.as_view(),
        name="appointment_update",
    ),
    path(
        "data/appointments/<int:pk>/delete/",
        views.AppointmentDeleteView.as_view(),
        name="appointment_delete",
    ),
    # Factures
    path("data/invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path(
        "data/invoices/new/", views.InvoiceCreateView.as_view(), name="invoice_create"
    ),
    path(
        "data/invoices/<int:pk>/edit/",
        views.InvoiceUpdateView.as_view(),
        name="invoice_update",
    ),
    path(
        "data/invoices/<int:pk>/delete/",
        views.InvoiceDeleteView.as_view(),
        name="invoice_delete",
    ),
    # Paiements
    path("data/payments/", views.PaymentListView.as_view(), name="payment_list"),
    path(
        "data/payments/new/", views.PaymentCreateView.as_view(), name="payment_create"
    ),
    path(
        "data/payments/<int:pk>/edit/",
        views.PaymentUpdateView.as_view(),
        name="payment_update",
    ),
    path(
        "data/payments/<int:pk>/delete/",
        views.PaymentDeleteView.as_view(),
        name="payment_delete",
    ),
]
