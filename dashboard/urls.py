from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.DashboardLoginView.as_view(), name="login"),
    path("logout/", views.DashboardLogoutView.as_view(), name="logout"),
    path("", views.overview, name="overview"),
    path("appointments/", views.appointment_list, name="appointments"),
    path("appointments/<int:pk>/confirm/", views.appointment_confirm, name="appointment_confirm"),
    path("appointments/<int:pk>/cancel/", views.appointment_cancel, name="appointment_cancel"),
    path(
        "appointments/<int:pk>/reschedule/",
        views.appointment_reschedule,
        name="appointment_reschedule",
    ),
    path(
        "appointments/<int:pk>/reschedule/<str:start_iso>/",
        views.appointment_reschedule_confirm,
        name="appointment_reschedule_confirm",
    ),
    path(
        "appointments/<int:pk>/open-case/",
        views.appointment_open_case,
        name="appointment_open_case",
    ),
    path("cases/", views.case_list, name="cases"),
    path("cases/<int:pk>/", views.case_detail, name="case_detail"),
    path("invoices/<int:pk>/toggle-paid/", views.invoice_toggle_paid, name="invoice_toggle_paid"),
]
