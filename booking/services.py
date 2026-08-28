import datetime as dt

from django.utils import timezone

from .models import Appointment
from team.models import Lawyer

SLOT_TIMES = [
    dt.time(9, 0),
    dt.time(10, 0),
    dt.time(11, 0),
    dt.time(12, 0),
    dt.time(14, 0),
    dt.time(15, 0),
    dt.time(16, 0),
]

BOOKING_LEAD_DAYS = 1
DAYS_TO_SCAN = 21
MAX_DAYS_WITH_SLOTS = 5


def lawyers_for_area(area):
    return list(Lawyer.objects.filter(practice_areas=area, is_active=True))


def get_available_slots(area, lawyer=None):
    """Return {date: [{"start": datetime, "lawyer": Lawyer}, ...]} of open slots.

    If `lawyer` is None, any active lawyer covering `area` may fill the slot —
    the first one free at that time is offered.
    """
    candidates = [lawyer] if lawyer else lawyers_for_area(area)
    if not candidates:
        return {}

    today = timezone.localdate()
    window_end = today + dt.timedelta(days=DAYS_TO_SCAN)
    booked = Appointment.objects.filter(
        lawyer__in=candidates,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        start_time__date__gte=today,
        start_time__date__lte=window_end,
    ).values_list("lawyer_id", "start_time")
    booked_set = set(booked)

    slots_by_day = {}
    for offset in range(BOOKING_LEAD_DAYS, DAYS_TO_SCAN + 1):
        day = today + dt.timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        day_slots = []
        for slot_time in SLOT_TIMES:
            start = timezone.make_aware(dt.datetime.combine(day, slot_time))
            for candidate in candidates:
                if (candidate.id, start) not in booked_set:
                    day_slots.append({"start": start, "lawyer": candidate})
                    break
        if day_slots:
            slots_by_day[day] = day_slots
        if len(slots_by_day) >= MAX_DAYS_WITH_SLOTS:
            break
    return slots_by_day
