from django.urls import path

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.start, name="start"),
    path("booked/<int:pk>/", views.confirmation, name="confirmation"),
    path("booked/<int:pk>/calendar.ics", views.appointment_ics, name="appointment_ics"),
    path("<slug:area_slug>/", views.choose_lawyer, name="choose_lawyer"),
    path("<slug:area_slug>/<str:lawyer_key>/", views.choose_slot, name="choose_slot"),
    path(
        "<slug:area_slug>/<int:lawyer_id>/<str:start_iso>/confirm/",
        views.confirm,
        name="confirm",
    ),
]
