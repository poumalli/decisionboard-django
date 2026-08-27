"""
Formulaires ModelForm pour les entités OLTP du cabinet.
"""

from django import forms

from .models import Appointment, Client, Employee, Invoice, Payment, Service


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "company_name",
            "contact_name",
            "email",
            "phone",
            "address",
            "city",
            "sector",
        ]
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "sector": forms.Select(attrs={"class": "form-control"}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "hire_date",
            "hourly_rate",
            "is_active",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "hire_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "hourly_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "category", "base_price", "duration_hours", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "base_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "duration_hours": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "client",
            "employee",
            "service",
            "date",
            "duration_hours",
            "status",
            "notes",
        ]
        widgets = {
            "client": forms.Select(attrs={"class": "form-control"}),
            "employee": forms.Select(attrs={"class": "form-control"}),
            "service": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "duration_hours": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "appointment",
            "invoice_number",
            "amount_ht",
            "tax_rate",
            "amount_ttc",
            "issued_date",
            "due_date",
            "status",
        ]
        widgets = {
            "appointment": forms.Select(attrs={"class": "form-control"}),
            "invoice_number": forms.TextInput(attrs={"class": "form-control"}),
            "amount_ht": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "tax_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "amount_ttc": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "issued_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["invoice", "amount", "payment_date", "method"]
        widgets = {
            "invoice": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "payment_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "method": forms.Select(attrs={"class": "form-control"}),
        }
