import datetime as dt

from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from config.antispam import is_rate_limited
from practice_areas.models import PracticeArea
from team.models import Lawyer

from .forms import AppointmentContactForm
from .models import Appointment
from .services import get_available_slots, has_conflicting_appointment, lawyers_for_area


def _get_lawyer_or_404(lawyer_pk, area):
    """Like get_object_or_404, but 404s on a non-numeric pk instead of
    crashing with a 500 (Lawyer's pk is an integer, and this value often
    comes straight from a URL segment or query string)."""
    if not str(lawyer_pk).isdigit():
        raise Http404("Invalid lawyer.")
    return get_object_or_404(Lawyer, pk=lawyer_pk, practice_areas=area, is_active=True)


def start(request):
    areas = PracticeArea.objects.filter(is_active=True)
    selected_slug = request.GET.get("area")
    if selected_slug:
        get_object_or_404(PracticeArea, slug=selected_slug, is_active=True)
        return redirect("booking:choose_lawyer", area_slug=selected_slug)
    return render(
        request,
        "booking/start.html",
        {"areas": areas, "active_nav": "booking", "current_step": 1},
    )


def choose_lawyer(request, area_slug):
    area = get_object_or_404(PracticeArea, slug=area_slug, is_active=True)
    lawyers = lawyers_for_area(area)
    selected = request.GET.get("lawyer")
    if selected:
        if selected != "any":
            _get_lawyer_or_404(selected, area)
        return redirect("booking:choose_slot", area_slug=area_slug, lawyer_key=selected)
    return render(
        request,
        "booking/choose_lawyer.html",
        {"area": area, "lawyers": lawyers, "active_nav": "booking", "current_step": 2},
    )


def choose_slot(request, area_slug, lawyer_key):
    area = get_object_or_404(PracticeArea, slug=area_slug, is_active=True)
    lawyer = None
    if lawyer_key != "any":
        lawyer = _get_lawyer_or_404(lawyer_key, area)
    slots_by_day = get_available_slots(area, lawyer)
    return render(
        request,
        "booking/choose_slot.html",
        {
            "area": area,
            "lawyer": lawyer,
            "lawyer_key": lawyer_key,
            "slots_by_day": slots_by_day,
            "active_nav": "booking",
            "current_step": 3,
        },
    )


def confirm(request, area_slug, lawyer_id, start_iso):
    area = get_object_or_404(PracticeArea, slug=area_slug, is_active=True)
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id, practice_areas=area, is_active=True)
    # Carries the client's original step-2 choice ("any" or a specific
    # lawyer) through to a slot-collision retry, so someone with no
    # preference isn't silently pinned to the one lawyer who just got
    # booked out from under them.
    lawyer_key = request.GET.get("pref") or str(lawyer_id)
    try:
        naive_start = dt.datetime.strptime(start_iso, "%Y%m%d%H%M")
        start_time = timezone.make_aware(naive_start)
    except ValueError:
        start_time = None

    slot_taken = start_time is None or Appointment.objects.filter(
        lawyer=lawyer,
        start_time=start_time,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
    ).exists()

    form = AppointmentContactForm(request.POST or None)

    if request.method == "POST" and not slot_taken and form.is_valid():
        if form.is_spam() or is_rate_limited(request, "booking", limit=8):
            # Treat it the same as a taken slot - no need to reveal to a bot
            # that it got caught, and no fake data to fabricate.
            slot_taken = True
        else:
            try:
                with transaction.atomic():
                    if has_conflicting_appointment(lawyer, start_time):
                        slot_taken = True
                    else:
                        appointment = form.save(commit=False)
                        appointment.practice_area = area
                        appointment.lawyer = lawyer
                        appointment.start_time = start_time
                        appointment.save()
                        return redirect(
                            "booking:confirmation", token=appointment.confirmation_token
                        )
            except IntegrityError:
                slot_taken = True

    return render(
        request,
        "booking/confirm.html",
        {
            "area": area,
            "lawyer": lawyer,
            "start_time": start_time,
            "form": form,
            "slot_taken": slot_taken,
            "lawyer_key": lawyer_key,
            "active_nav": "booking",
            "current_step": 4,
        },
    )


def confirmation(request, token):
    appointment = get_object_or_404(Appointment, confirmation_token=token)
    return render(
        request,
        "booking/confirmation.html",
        {"appointment": appointment, "active_nav": "booking"},
    )


def _ics_datetime(value):
    return value.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def appointment_ics(request, token):
    appointment = get_object_or_404(Appointment, confirmation_token=token)
    start = appointment.start_time
    end = start + dt.timedelta(minutes=30)
    lawyer_name = appointment.lawyer.name if appointment.lawyer else "one of our lawyers"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Cassian & Voicu//Booking//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:appointment-{appointment.pk}@cassianvoicu.example",
        f"DTSTAMP:{_ics_datetime(timezone.now())}",
        f"DTSTART:{_ics_datetime(start)}",
        f"DTEND:{_ics_datetime(end)}",
        f"SUMMARY:Consultation — {appointment.practice_area.name} — Cassian \\& Voicu",
        f"DESCRIPTION:Initial consultation with {lawyer_name}.",
        "LOCATION:14 Calea Victoriei\\, 3rd Floor\\, Bucharest\\, Romania",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    content = "\r\n".join(lines) + "\r\n"

    response = HttpResponse(content, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="consultation.ics"'
    return response
