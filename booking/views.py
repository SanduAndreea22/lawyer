import datetime as dt

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from practice_areas.models import PracticeArea
from team.models import Lawyer

from .forms import AppointmentContactForm
from .models import Appointment
from .services import get_available_slots, lawyers_for_area


def start(request):
    areas = PracticeArea.objects.filter(is_active=True)
    selected_slug = request.GET.get("area")
    if selected_slug:
        get_object_or_404(PracticeArea, slug=selected_slug, is_active=True)
        return redirect("booking:choose_lawyer", area_slug=selected_slug)
    return render(
        request,
        "booking/start.html",
        {"areas": areas, "active_nav": "booking"},
    )


def choose_lawyer(request, area_slug):
    area = get_object_or_404(PracticeArea, slug=area_slug, is_active=True)
    lawyers = lawyers_for_area(area)
    selected = request.GET.get("lawyer")
    if selected:
        if selected != "any":
            get_object_or_404(Lawyer, pk=selected, practice_areas=area, is_active=True)
        return redirect("booking:choose_slot", area_slug=area_slug, lawyer_key=selected)
    return render(
        request,
        "booking/choose_lawyer.html",
        {"area": area, "lawyers": lawyers, "active_nav": "booking"},
    )


def choose_slot(request, area_slug, lawyer_key):
    area = get_object_or_404(PracticeArea, slug=area_slug, is_active=True)
    lawyer = None
    if lawyer_key != "any":
        lawyer = get_object_or_404(
            Lawyer, pk=lawyer_key, practice_areas=area, is_active=True
        )
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
        },
    )


def confirm(request, area_slug, lawyer_id, start_iso):
    area = get_object_or_404(PracticeArea, slug=area_slug, is_active=True)
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id, practice_areas=area, is_active=True)
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

    if request.method == "POST" and not slot_taken:
        if form.is_valid():
            try:
                with transaction.atomic():
                    conflict = (
                        Appointment.objects.select_for_update()
                        .filter(
                            lawyer=lawyer,
                            start_time=start_time,
                            status__in=[
                                Appointment.Status.PENDING,
                                Appointment.Status.CONFIRMED,
                            ],
                        )
                        .exists()
                    )
                    if conflict:
                        slot_taken = True
                    else:
                        appointment = form.save(commit=False)
                        appointment.practice_area = area
                        appointment.lawyer = lawyer
                        appointment.start_time = start_time
                        appointment.save()
                        return redirect("booking:confirmation", pk=appointment.pk)
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
            "active_nav": "booking",
        },
    )


def confirmation(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(
        request,
        "booking/confirmation.html",
        {"appointment": appointment, "active_nav": "booking"},
    )
