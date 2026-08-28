from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def is_full_staff(user):
    """Front-desk / admin accounts that may see every lawyer's data.

    Deliberately narrower than Django's `is_staff` flag (which only
    controls /admin/ access) - an individual lawyer can be `is_staff`
    for admin purposes without that unlocking every other lawyer's
    appointments and cases in the dashboard.
    """
    return user.is_authenticated and user.is_superuser


def user_lawyer(user):
    return getattr(user, "lawyer_profile", None)


def staff_or_lawyer_required(view_func):
    """Only staff accounts or accounts linked to a Lawyer profile may in."""

    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_staff or is_full_staff(request.user) or user_lawyer(request.user)):
            raise PermissionDenied("This area is for firm staff only.")
        return view_func(request, *args, **kwargs)

    return wrapped
