"""Tests — core/views.py : CRUD des entités OLTP."""

from datetime import date

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client as HttpClient

from core.models import Appointment, Client, Employee, Invoice, Payment, Service


@pytest.fixture
def admin_client_(db):
    user = User.objects.create_user(username="admin", password="p")
    group, _ = Group.objects.get_or_create(name="Administrateur")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="admin", password="p")
    return client


@pytest.fixture
def consultant_client_(db):
    user = User.objects.create_user(username="cons", password="p")
    group, _ = Group.objects.get_or_create(name="Consultant")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="cons", password="p")
    return client


LIST_URLS = [
    "/data/clients/",
    "/data/employees/",
    "/data/services/",
    "/data/appointments/",
    "/data/invoices/",
    "/data/payments/",
]


@pytest.mark.django_db(databases=["default", "dw"])
class TestCRUDListPagesRenderForAdmin:

    @pytest.mark.parametrize("url", LIST_URLS)
    def test_list_page_returns_200_for_admin(self, admin_client_, url):
        response = admin_client_.get(url)
        assert response.status_code == 200


@pytest.mark.django_db(databases=["default", "dw"])
class TestCRUDListPagesForbiddenForConsultant:

    @pytest.mark.parametrize("url", LIST_URLS)
    def test_list_page_returns_403_for_consultant(self, consultant_client_, url):
        response = consultant_client_.get(url)
        assert response.status_code == 403


@pytest.mark.django_db(databases=["default", "dw"])
class TestClientCRUDRoundTrip:

    def test_create_client_then_appears_in_list(self, admin_client_):
        response = admin_client_.post(
            "/data/clients/new/",
            {
                "company_name": "Nouvelle Société SA",
                "contact_name": "Jean Dupont",
                "email": "jean@nouvelle-societe.ch",
                "phone": "+41 21 000 00 00",
                "address": "Rue Example 1",
                "city": "Genève",
                "sector": "tech",
            },
        )
        assert response.status_code == 302
        assert Client.objects.filter(company_name="Nouvelle Société SA").exists()
        list_response = admin_client_.get("/data/clients/")
        assert "Nouvelle Société SA" in list_response.content.decode()

    def test_update_client_changes_company_name(self, admin_client_):
        client_obj = Client.objects.create(
            company_name="Ancien Nom",
            contact_name="A",
            email="ancien@test.ch",
            sector="tech",
        )
        response = admin_client_.post(
            f"/data/clients/{client_obj.pk}/edit/",
            {
                "company_name": "Nom Modifié",
                "contact_name": "A",
                "email": "ancien@test.ch",
                "phone": "",
                "address": "",
                "city": "",
                "sector": "tech",
            },
        )
        assert response.status_code == 302
        client_obj.refresh_from_db()
        assert client_obj.company_name == "Nom Modifié"

    def test_delete_client_removes_it(self, admin_client_):
        client_obj = Client.objects.create(
            company_name="À Supprimer",
            contact_name="A",
            email="supprimer@test.ch",
            sector="tech",
        )
        response = admin_client_.post(f"/data/clients/{client_obj.pk}/delete/")
        assert response.status_code == 302
        assert not Client.objects.filter(pk=client_obj.pk).exists()


@pytest.fixture
def sample_invoice(db):
    client_obj = Client.objects.create(
        company_name="Client Test", contact_name="A", email="a@test.ch", sector="tech"
    )
    employee = Employee.objects.create(
        first_name="Jean",
        last_name="Test",
        email="jean@test.ch",
        role="senior",
        hire_date=date(2020, 1, 1),
        hourly_rate=150,
    )
    service = Service.objects.create(
        name="Service Test", category="it", base_price=1000, duration_hours=10
    )
    appointment = Appointment.objects.create(
        client=client_obj,
        employee=employee,
        service=service,
        date=date(2026, 1, 1),
        duration_hours=10,
        status="realise",
    )
    return Invoice.objects.create(
        appointment=appointment,
        invoice_number="AUD-TEST-0001",
        amount_ht=1000,
        amount_ttc=1200,
        issued_date=date(2026, 1, 5),
        due_date=date(2026, 2, 5),
        status="emise",
    )


@pytest.mark.django_db(databases=["default", "dw"])
class TestPaymentCRUDRoundTrip:

    def test_create_payment_then_appears_in_list(self, admin_client_, sample_invoice):
        response = admin_client_.post(
            "/data/payments/new/",
            {
                "invoice": sample_invoice.pk,
                "amount": "1200.00",
                "payment_date": "2026-02-01",
                "method": "virement",
            },
        )
        assert response.status_code == 302
        assert Payment.objects.filter(invoice=sample_invoice).exists()
        list_response = admin_client_.get("/data/payments/")
        assert "AUD-TEST-0001" in list_response.content.decode()

    def test_update_payment_changes_amount(self, admin_client_, sample_invoice):
        payment = Payment.objects.create(
            invoice=sample_invoice,
            amount=1200,
            payment_date=date(2026, 2, 1),
            method="virement",
        )
        response = admin_client_.post(
            f"/data/payments/{payment.pk}/edit/",
            {
                "invoice": sample_invoice.pk,
                "amount": "999.00",
                "payment_date": "2026-02-01",
                "method": "carte",
            },
        )
        assert response.status_code == 302
        payment.refresh_from_db()
        assert payment.amount == 999

    def test_delete_payment_removes_it(self, admin_client_, sample_invoice):
        payment = Payment.objects.create(
            invoice=sample_invoice,
            amount=1200,
            payment_date=date(2026, 2, 1),
            method="virement",
        )
        response = admin_client_.post(f"/data/payments/{payment.pk}/delete/")
        assert response.status_code == 302
        assert not Payment.objects.filter(pk=payment.pk).exists()


@pytest.mark.django_db(databases=["default", "dw"])
class TestClientDetailView:

    def test_admin_sees_client_detail_with_mission_history(self, admin_client_):
        client_obj = Client.objects.create(
            company_name="Client Historique",
            contact_name="A",
            email="hist@test.ch",
            sector="tech",
        )
        employee = Employee.objects.create(
            first_name="Ana",
            last_name="Ex",
            email="ana@test.ch",
            role="senior",
            hire_date=date(2020, 1, 1),
            hourly_rate=150,
        )
        service = Service.objects.create(
            name="Mission Historique", category="it", base_price=500, duration_hours=5
        )
        Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="realise",
        )
        response = admin_client_.get(f"/data/clients/{client_obj.pk}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Client Historique" in content
        assert "Mission Historique" in content

    def test_consultant_forbidden_from_client_detail(self, consultant_client_):
        client_obj = Client.objects.create(
            company_name="Client X", contact_name="A", email="x@test.ch", sector="tech"
        )
        response = consultant_client_.get(f"/data/clients/{client_obj.pk}/")
        assert response.status_code == 403


@pytest.mark.django_db(databases=["default", "dw"])
class TestEmployeeDetailView:

    def test_admin_sees_employee_detail_with_mission_history(self, admin_client_):
        client_obj = Client.objects.create(
            company_name="Client Y", contact_name="A", email="y@test.ch", sector="tech"
        )
        employee = Employee.objects.create(
            first_name="Marc",
            last_name="Consultant",
            email="marc@test.ch",
            role="manager",
            hire_date=date(2019, 1, 1),
            hourly_rate=200,
        )
        service = Service.objects.create(
            name="Audit Historique",
            category="finance",
            base_price=800,
            duration_hours=8,
        )
        Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=8,
            status="realise",
        )
        response = admin_client_.get(f"/data/employees/{employee.pk}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Marc" in content
        assert "Audit Historique" in content


@pytest.mark.django_db(databases=["default", "dw"])
class TestEmployeeCRUDRoundTrip:

    def test_create_employee_then_appears_in_list(self, admin_client_):
        response = admin_client_.post(
            "/data/employees/new/",
            {
                "first_name": "Nouveau",
                "last_name": "Consultant",
                "email": "nouveau@test.ch",
                "role": "consultant",
                "hire_date": "2026-01-01",
                "hourly_rate": "120",
                "is_active": "on",
            },
        )
        assert response.status_code == 302
        assert Employee.objects.filter(email="nouveau@test.ch").exists()

    def test_update_employee_changes_role(self, admin_client_):
        employee = Employee.objects.create(
            first_name="A",
            last_name="B",
            email="ab@test.ch",
            role="consultant",
            hire_date=date(2020, 1, 1),
            hourly_rate=100,
        )
        response = admin_client_.post(
            f"/data/employees/{employee.pk}/edit/",
            {
                "first_name": "A",
                "last_name": "B",
                "email": "ab@test.ch",
                "role": "manager",
                "hire_date": "2020-01-01",
                "hourly_rate": "100",
            },
        )
        assert response.status_code == 302
        employee.refresh_from_db()
        assert employee.role == "manager"

    def test_delete_employee_removes_it(self, admin_client_):
        employee = Employee.objects.create(
            first_name="A",
            last_name="Suppr",
            email="asuppr@test.ch",
            role="consultant",
            hire_date=date(2020, 1, 1),
            hourly_rate=100,
        )
        response = admin_client_.post(f"/data/employees/{employee.pk}/delete/")
        assert response.status_code == 302
        assert not Employee.objects.filter(pk=employee.pk).exists()


@pytest.mark.django_db(databases=["default", "dw"])
class TestServiceCRUDRoundTrip:

    def test_create_service_then_appears_in_list(self, admin_client_):
        response = admin_client_.post(
            "/data/services/new/",
            {
                "name": "Nouveau Service",
                "category": "it",
                "base_price": "500",
                "duration_hours": "5",
                "description": "",
            },
        )
        assert response.status_code == 302
        assert Service.objects.filter(name="Nouveau Service").exists()

    def test_update_service_changes_price(self, admin_client_):
        service = Service.objects.create(
            name="Service X", category="it", base_price=500, duration_hours=5
        )
        response = admin_client_.post(
            f"/data/services/{service.pk}/edit/",
            {
                "name": "Service X",
                "category": "it",
                "base_price": "999",
                "duration_hours": "5",
                "description": "",
            },
        )
        assert response.status_code == 302
        service.refresh_from_db()
        assert service.base_price == 999

    def test_delete_service_removes_it(self, admin_client_):
        service = Service.objects.create(
            name="À supprimer", category="it", base_price=500, duration_hours=5
        )
        response = admin_client_.post(f"/data/services/{service.pk}/delete/")
        assert response.status_code == 302
        assert not Service.objects.filter(pk=service.pk).exists()


@pytest.fixture
def sample_appointment_deps(db):
    client_obj = Client.objects.create(
        company_name="Client Dep", contact_name="A", email="dep@test.ch", sector="tech"
    )
    employee = Employee.objects.create(
        first_name="Dep",
        last_name="Employee",
        email="depemp@test.ch",
        role="consultant",
        hire_date=date(2020, 1, 1),
        hourly_rate=100,
    )
    service = Service.objects.create(
        name="Service Dep", category="it", base_price=500, duration_hours=5
    )
    return client_obj, employee, service


@pytest.mark.django_db(databases=["default", "dw"])
class TestAppointmentCRUDRoundTrip:

    def test_create_appointment_then_appears_in_list(
        self, admin_client_, sample_appointment_deps
    ):
        client_obj, employee, service = sample_appointment_deps
        response = admin_client_.post(
            "/data/appointments/new/",
            {
                "client": client_obj.pk,
                "employee": employee.pk,
                "service": service.pk,
                "date": "2026-01-01",
                "duration_hours": "5",
                "status": "planifie",
                "notes": "",
            },
        )
        assert response.status_code == 302
        assert Appointment.objects.filter(client=client_obj).exists()

    def test_update_appointment_changes_status(
        self, admin_client_, sample_appointment_deps
    ):
        client_obj, employee, service = sample_appointment_deps
        appointment = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="planifie",
        )
        response = admin_client_.post(
            f"/data/appointments/{appointment.pk}/edit/",
            {
                "client": client_obj.pk,
                "employee": employee.pk,
                "service": service.pk,
                "date": "2026-01-01",
                "duration_hours": "5",
                "status": "realise",
                "notes": "",
            },
        )
        assert response.status_code == 302
        appointment.refresh_from_db()
        assert appointment.status == "realise"

    def test_delete_appointment_removes_it(
        self, admin_client_, sample_appointment_deps
    ):
        client_obj, employee, service = sample_appointment_deps
        appointment = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="planifie",
        )
        response = admin_client_.post(f"/data/appointments/{appointment.pk}/delete/")
        assert response.status_code == 302
        assert not Appointment.objects.filter(pk=appointment.pk).exists()


@pytest.mark.django_db(databases=["default", "dw"])
class TestInvoiceCRUDRoundTrip:

    def test_create_invoice_then_appears_in_list(
        self, admin_client_, sample_appointment_deps
    ):
        client_obj, employee, service = sample_appointment_deps
        appointment = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="realise",
        )
        response = admin_client_.post(
            "/data/invoices/new/",
            {
                "appointment": appointment.pk,
                "invoice_number": "AUD-NEW-0001",
                "amount_ht": "500",
                "tax_rate": "20",
                "amount_ttc": "600",
                "issued_date": "2026-01-05",
                "due_date": "2026-02-05",
                "status": "emise",
            },
        )
        assert response.status_code == 302
        assert Invoice.objects.filter(invoice_number="AUD-NEW-0001").exists()

    def test_update_invoice_changes_status(
        self, admin_client_, sample_appointment_deps
    ):
        client_obj, employee, service = sample_appointment_deps
        appointment = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="realise",
        )
        invoice = Invoice.objects.create(
            appointment=appointment,
            invoice_number="AUD-UPD-0001",
            amount_ht=500,
            amount_ttc=600,
            issued_date=date(2026, 1, 5),
            due_date=date(2026, 2, 5),
            status="emise",
        )
        response = admin_client_.post(
            f"/data/invoices/{invoice.pk}/edit/",
            {
                "appointment": appointment.pk,
                "invoice_number": "AUD-UPD-0001",
                "amount_ht": "500",
                "tax_rate": "20",
                "amount_ttc": "600",
                "issued_date": "2026-01-05",
                "due_date": "2026-02-05",
                "status": "payee",
            },
        )
        assert response.status_code == 302
        invoice.refresh_from_db()
        assert invoice.status == "payee"

    def test_delete_invoice_removes_it(self, admin_client_, sample_appointment_deps):
        client_obj, employee, service = sample_appointment_deps
        appointment = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="realise",
        )
        invoice = Invoice.objects.create(
            appointment=appointment,
            invoice_number="AUD-DEL-0001",
            amount_ht=500,
            amount_ttc=600,
            issued_date=date(2026, 1, 5),
            due_date=date(2026, 2, 5),
        )
        response = admin_client_.post(f"/data/invoices/{invoice.pk}/delete/")
        assert response.status_code == 302
        assert not Invoice.objects.filter(pk=invoice.pk).exists()


@pytest.mark.django_db(databases=["default", "dw"])
class TestConfirmDeletePagesShowObjectLabel:
    """GET sur les pages de confirmation — couvre object_label/cancel_url."""

    def test_client_confirm_delete_page(self, admin_client_):
        obj = Client.objects.create(
            company_name="Confirm Client",
            contact_name="A",
            email="confirm@test.ch",
            sector="tech",
        )
        response = admin_client_.get(f"/data/clients/{obj.pk}/delete/")
        assert response.status_code == 200
        assert "Confirm Client" in response.content.decode()

    def test_employee_confirm_delete_page(self, admin_client_):
        obj = Employee.objects.create(
            first_name="Confirm",
            last_name="Employee",
            email="confirmemp@test.ch",
            role="consultant",
            hire_date=date(2020, 1, 1),
            hourly_rate=100,
        )
        response = admin_client_.get(f"/data/employees/{obj.pk}/delete/")
        assert response.status_code == 200
        assert "Confirm Employee" in response.content.decode()

    def test_service_confirm_delete_page(self, admin_client_):
        obj = Service.objects.create(
            name="Confirm Service", category="it", base_price=500, duration_hours=5
        )
        response = admin_client_.get(f"/data/services/{obj.pk}/delete/")
        assert response.status_code == 200
        assert "Confirm Service" in response.content.decode()

    def test_appointment_confirm_delete_page(
        self, admin_client_, sample_appointment_deps
    ):
        client_obj, employee, service = sample_appointment_deps
        obj = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="planifie",
        )
        response = admin_client_.get(f"/data/appointments/{obj.pk}/delete/")
        assert response.status_code == 200

    def test_invoice_confirm_delete_page(self, admin_client_, sample_appointment_deps):
        client_obj, employee, service = sample_appointment_deps
        appointment = Appointment.objects.create(
            client=client_obj,
            employee=employee,
            service=service,
            date=date(2026, 1, 1),
            duration_hours=5,
            status="realise",
        )
        obj = Invoice.objects.create(
            appointment=appointment,
            invoice_number="AUD-CONFIRM-0001",
            amount_ht=500,
            amount_ttc=600,
            issued_date=date(2026, 1, 5),
            due_date=date(2026, 2, 5),
        )
        response = admin_client_.get(f"/data/invoices/{obj.pk}/delete/")
        assert response.status_code == 200
        assert "AUD-CONFIRM-0001" in response.content.decode()

    def test_payment_confirm_delete_page(self, admin_client_, sample_invoice):
        obj = Payment.objects.create(
            invoice=sample_invoice,
            amount=1200,
            payment_date=date(2026, 2, 1),
            method="virement",
        )
        response = admin_client_.get(f"/data/payments/{obj.pk}/delete/")
        assert response.status_code == 200
