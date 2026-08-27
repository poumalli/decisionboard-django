"""
Vues CRUD pour les entités OLTP.
Accès restreint aux administrateurs uniquement.
"""

from django.contrib import messages
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .forms import (
    AppointmentForm,
    ClientForm,
    EmployeeForm,
    InvoiceForm,
    PaymentForm,
    ServiceForm,
)
from .models import Appointment, Client, Employee, Invoice, Payment, Service
from .permissions import admin_required


# ---------------------------------------------------------------------------
# Contexte partagé — section active pour le sous-menu de la page Données
#
# Combiner ces mixins à des CBV Django fait remonter des faux positifs mypy
# ("misc": extra_context/object incompatibles avec ContextMixin/DeletionMixin)
# — limitation connue de django-stubs avec l'héritage multiple, sans impact à
# l'exécution. Désactivé pour ce module via mypy.ini plutôt que de disperser
# des `# type: ignore` sur chacune des 20 classes concernées.
# ---------------------------------------------------------------------------


class ClientSectionMixin:
    extra_context = {"page": "data", "section": "clients"}


class EmployeeSectionMixin:
    extra_context = {"page": "data", "section": "employees"}


class ServiceSectionMixin:
    extra_context = {"page": "data", "section": "services"}


class AppointmentSectionMixin:
    extra_context = {
        "page": "data",
        "section": "appointments",
    }


class InvoiceSectionMixin:
    extra_context = {"page": "data", "section": "invoices"}


class PaymentSectionMixin:
    extra_context = {"page": "data", "section": "payments"}


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


@method_decorator(admin_required, name="dispatch")
class ClientListView(ClientSectionMixin, ListView):
    model = Client
    template_name = "core/client_list.html"
    context_object_name = "clients"
    paginate_by = 25


@method_decorator(admin_required, name="dispatch")
class ClientCreateView(ClientSectionMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "core/client_form.html"
    success_url = reverse_lazy("core:client_list")

    def form_valid(self, form):
        messages.success(self.request, "Client créé avec succès.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class ClientUpdateView(ClientSectionMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "core/client_form.html"
    success_url = reverse_lazy("core:client_list")

    def form_valid(self, form):
        messages.success(self.request, "Client mis à jour.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class ClientDeleteView(ClientSectionMixin, DeleteView):
    model = Client
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("core:client_list")

    def form_valid(self, form):
        messages.success(self.request, "Client supprimé.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = str(self.object)
        ctx["cancel_url"] = reverse_lazy("core:client_list")
        return ctx


@method_decorator(admin_required, name="dispatch")
class ClientDetailView(ClientSectionMixin, DetailView):
    model = Client
    template_name = "core/client_detail.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["appointments"] = self.object.appointment_set.select_related(
            "service", "employee"
        ).order_by("-date")
        return ctx


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------


@method_decorator(admin_required, name="dispatch")
class EmployeeListView(EmployeeSectionMixin, ListView):
    model = Employee
    template_name = "core/employee_list.html"
    context_object_name = "employees"
    paginate_by = 25


@method_decorator(admin_required, name="dispatch")
class EmployeeCreateView(EmployeeSectionMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "core/employee_form.html"
    success_url = reverse_lazy("core:employee_list")

    def form_valid(self, form):
        messages.success(self.request, "Consultant créé avec succès.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class EmployeeUpdateView(EmployeeSectionMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "core/employee_form.html"
    success_url = reverse_lazy("core:employee_list")

    def form_valid(self, form):
        messages.success(self.request, "Consultant mis à jour.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class EmployeeDeleteView(EmployeeSectionMixin, DeleteView):
    model = Employee
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("core:employee_list")

    def form_valid(self, form):
        messages.success(self.request, "Consultant supprimé.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = str(self.object)
        ctx["cancel_url"] = reverse_lazy("core:employee_list")
        return ctx


@method_decorator(admin_required, name="dispatch")
class EmployeeDetailView(EmployeeSectionMixin, DetailView):
    model = Employee
    template_name = "core/employee_detail.html"
    context_object_name = "employee"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["appointments"] = self.object.appointment_set.select_related(
            "service", "client"
        ).order_by("-date")
        return ctx


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


@method_decorator(admin_required, name="dispatch")
class ServiceListView(ServiceSectionMixin, ListView):
    model = Service
    template_name = "core/service_list.html"
    context_object_name = "services"
    paginate_by = 25


@method_decorator(admin_required, name="dispatch")
class ServiceCreateView(ServiceSectionMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "core/service_form.html"
    success_url = reverse_lazy("core:service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service créé avec succès.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class ServiceUpdateView(ServiceSectionMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "core/service_form.html"
    success_url = reverse_lazy("core:service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service mis à jour.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class ServiceDeleteView(ServiceSectionMixin, DeleteView):
    model = Service
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("core:service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service supprimé.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = str(self.object)
        ctx["cancel_url"] = reverse_lazy("core:service_list")
        return ctx


# ---------------------------------------------------------------------------
# Appointment
# ---------------------------------------------------------------------------


@method_decorator(admin_required, name="dispatch")
class AppointmentListView(AppointmentSectionMixin, ListView):
    model = Appointment
    template_name = "core/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 25

    def get_queryset(self):
        return Appointment.objects.select_related("client", "employee", "service")


@method_decorator(admin_required, name="dispatch")
class AppointmentCreateView(AppointmentSectionMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "core/appointment_form.html"
    success_url = reverse_lazy("core:appointment_list")

    def form_valid(self, form):
        messages.success(self.request, "Mission créée avec succès.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class AppointmentUpdateView(AppointmentSectionMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "core/appointment_form.html"
    success_url = reverse_lazy("core:appointment_list")

    def form_valid(self, form):
        messages.success(self.request, "Mission mise à jour.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class AppointmentDeleteView(AppointmentSectionMixin, DeleteView):
    model = Appointment
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("core:appointment_list")

    def form_valid(self, form):
        messages.success(self.request, "Mission supprimée.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = str(self.object)
        ctx["cancel_url"] = reverse_lazy("core:appointment_list")
        return ctx


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------


@method_decorator(admin_required, name="dispatch")
class InvoiceListView(InvoiceSectionMixin, ListView):
    model = Invoice
    template_name = "core/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 25

    def get_queryset(self):
        return Invoice.objects.select_related("appointment__client")


@method_decorator(admin_required, name="dispatch")
class InvoiceCreateView(InvoiceSectionMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "core/invoice_form.html"
    success_url = reverse_lazy("core:invoice_list")

    def form_valid(self, form):
        messages.success(self.request, "Facture créée avec succès.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class InvoiceUpdateView(InvoiceSectionMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "core/invoice_form.html"
    success_url = reverse_lazy("core:invoice_list")

    def form_valid(self, form):
        messages.success(self.request, "Facture mise à jour.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class InvoiceDeleteView(InvoiceSectionMixin, DeleteView):
    model = Invoice
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("core:invoice_list")

    def form_valid(self, form):
        messages.success(self.request, "Facture supprimée.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = str(self.object)
        ctx["cancel_url"] = reverse_lazy("core:invoice_list")
        return ctx


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


@method_decorator(admin_required, name="dispatch")
class PaymentListView(PaymentSectionMixin, ListView):
    model = Payment
    template_name = "core/payment_list.html"
    context_object_name = "payments"
    paginate_by = 25

    def get_queryset(self):
        return Payment.objects.select_related("invoice__appointment__client")


@method_decorator(admin_required, name="dispatch")
class PaymentCreateView(PaymentSectionMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "core/payment_form.html"
    success_url = reverse_lazy("core:payment_list")

    def form_valid(self, form):
        messages.success(self.request, "Paiement créé avec succès.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class PaymentUpdateView(PaymentSectionMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = "core/payment_form.html"
    success_url = reverse_lazy("core:payment_list")

    def form_valid(self, form):
        messages.success(self.request, "Paiement mis à jour.")
        return super().form_valid(form)


@method_decorator(admin_required, name="dispatch")
class PaymentDeleteView(PaymentSectionMixin, DeleteView):
    model = Payment
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("core:payment_list")

    def form_valid(self, form):
        messages.success(self.request, "Paiement supprimé.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = str(self.object)
        ctx["cancel_url"] = reverse_lazy("core:payment_list")
        return ctx


# ---------------------------------------------------------------------------
# Handlers d'erreur globaux
# ---------------------------------------------------------------------------


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)
