import datetime as dt

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from booking.models import Appointment
from booking.services import get_available_slots

from .access import is_full_staff, staff_or_lawyer_required, user_lawyer
from .forms import CaseStatusForm, DocumentUploadForm
from .models import Case, Invoice


class DashboardLoginView(auth_views.LoginView):
    template_name = "dashboard/login.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_nav"] = "dashboard"
        return ctx


class DashboardLogoutView(auth_views.LogoutView):
    next_page = "pages:home"


def _visible_appointments(request):
    qs = Appointment.objects.select_related("practice_area", "lawyer")
    lawyer = user_lawyer(request.user)
    if lawyer and not is_full_staff(request.user):
        qs = qs.filter(lawyer=lawyer)
    return qs


def _visible_cases(request):
    qs = Case.objects.select_related("practice_area", "lawyer")
    lawyer = user_lawyer(request.user)
    if lawyer and not is_full_staff(request.user):
        qs = qs.filter(lawyer=lawyer)
    return qs


@staff_or_lawyer_required
def overview(request):
    now = timezone.now()
    upcoming = _visible_appointments(request).filter(
        start_time__gte=now, status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).order_by("start_time")[:8]
    active_cases = _visible_cases(request).exclude(status=Case.Status.CLOSED)[:8]
    unpaid_invoices = Invoice.objects.select_related("case").filter(
        status=Invoice.Status.UNPAID
    )
    if user_lawyer(request.user) and not is_full_staff(request.user):
        unpaid_invoices = unpaid_invoices.filter(case__lawyer=user_lawyer(request.user))
    unpaid_invoices = unpaid_invoices.order_by("due_date")[:8]

    return render(
        request,
        "dashboard/overview.html",
        {
            "upcoming": upcoming,
            "active_cases": active_cases,
            "unpaid_invoices": unpaid_invoices,
            "active_nav": "dashboard",
        },
    )


@staff_or_lawyer_required
def appointment_list(request):
    appointments = _visible_appointments(request).order_by("start_time")
    status_filter = request.GET.get("status")
    if status_filter in Appointment.Status.values:
        appointments = appointments.filter(status=status_filter)
    return render(
        request,
        "dashboard/appointments.html",
        {
            "appointments": appointments,
            "status_filter": status_filter,
            "statuses": Appointment.Status.choices,
            "active_nav": "dashboard",
        },
    )


def _get_visible_appointment(request, pk):
    return get_object_or_404(_visible_appointments(request), pk=pk)


@staff_or_lawyer_required
def appointment_confirm(request, pk):
    appointment = _get_visible_appointment(request, pk)
    if request.method == "POST":
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=["status"])
        messages.success(request, f"Appointment with {appointment.client_name} confirmed.")
    return redirect("dashboard:appointments")


@staff_or_lawyer_required
def appointment_cancel(request, pk):
    appointment = _get_visible_appointment(request, pk)
    if request.method == "POST":
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status"])
        messages.success(request, f"Appointment with {appointment.client_name} cancelled.")
    return redirect("dashboard:appointments")


@staff_or_lawyer_required
def appointment_reschedule(request, pk):
    appointment = _get_visible_appointment(request, pk)
    lawyer = appointment.lawyer
    slots_by_day = {}
    if lawyer:
        slots_by_day = get_available_slots(appointment.practice_area, lawyer)
    return render(
        request,
        "dashboard/reschedule.html",
        {"appointment": appointment, "slots_by_day": slots_by_day, "active_nav": "dashboard"},
    )


@staff_or_lawyer_required
def appointment_reschedule_confirm(request, pk, start_iso):
    appointment = _get_visible_appointment(request, pk)
    try:
        naive_start = dt.datetime.strptime(start_iso, "%Y%m%d%H%M")
        new_start = timezone.make_aware(naive_start)
    except ValueError:
        messages.error(request, "Invalid time slot.")
        return redirect("dashboard:appointment_reschedule", pk=pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                conflict = (
                    Appointment.objects.select_for_update()
                    .filter(
                        lawyer=appointment.lawyer,
                        start_time=new_start,
                        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
                    )
                    .exclude(pk=appointment.pk)
                    .exists()
                )
                if conflict:
                    messages.error(request, "That slot was just taken. Please choose another.")
                    return redirect("dashboard:appointment_reschedule", pk=pk)
                appointment.start_time = new_start
                appointment.save(update_fields=["start_time"])
        except IntegrityError:
            messages.error(request, "That slot was just taken. Please choose another.")
            return redirect("dashboard:appointment_reschedule", pk=pk)
        messages.success(request, "Appointment rescheduled.")
        return redirect("dashboard:appointments")

    return redirect("dashboard:appointment_reschedule", pk=pk)


@staff_or_lawyer_required
def appointment_open_case(request, pk):
    appointment = _get_visible_appointment(request, pk)
    if request.method == "POST":
        if hasattr(appointment, "cases") and appointment.cases.exists():
            case = appointment.cases.first()
        elif appointment.lawyer is None:
            messages.error(request, "Assign a lawyer to this appointment before opening a case.")
            return redirect("dashboard:appointments")
        else:
            case = Case.objects.create(
                client_name=appointment.client_name,
                client_phone=appointment.client_phone,
                lawyer=appointment.lawyer,
                practice_area=appointment.practice_area,
                description=appointment.note,
                appointment=appointment,
            )
        return redirect("dashboard:case_detail", pk=case.pk)
    return redirect("dashboard:appointments")


@staff_or_lawyer_required
def case_list(request):
    cases = _visible_cases(request)
    status_filter = request.GET.get("status")
    if status_filter in Case.Status.values:
        cases = cases.filter(status=status_filter)
    return render(
        request,
        "dashboard/cases.html",
        {
            "cases": cases,
            "status_filter": status_filter,
            "statuses": Case.Status.choices,
            "active_nav": "dashboard",
        },
    )


@staff_or_lawyer_required
def case_detail(request, pk):
    case = get_object_or_404(_visible_cases(request), pk=pk)
    status_form = CaseStatusForm(instance=case)
    upload_form = DocumentUploadForm()

    if request.method == "POST":
        if "update_status" in request.POST:
            status_form = CaseStatusForm(request.POST, instance=case)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Case updated.")
                return redirect("dashboard:case_detail", pk=case.pk)
        elif "upload_document" in request.POST:
            upload_form = DocumentUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                document = upload_form.save(commit=False)
                document.case = case
                document.save()
                messages.success(request, "Document uploaded.")
                return redirect("dashboard:case_detail", pk=case.pk)

    return render(
        request,
        "dashboard/case_detail.html",
        {
            "case": case,
            "status_form": status_form,
            "upload_form": upload_form,
            "documents": case.documents.all(),
            "invoices": case.invoices.all(),
            "active_nav": "dashboard",
        },
    )


@staff_or_lawyer_required
def invoice_toggle_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, case__in=_visible_cases(request))
    if request.method == "POST":
        invoice.status = (
            Invoice.Status.PAID if invoice.status == Invoice.Status.UNPAID else Invoice.Status.UNPAID
        )
        invoice.save(update_fields=["status"])
    return redirect("dashboard:case_detail", pk=invoice.case_id)
