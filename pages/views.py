from django.contrib import messages
from django.shortcuts import redirect, render

from practice_areas.models import PracticeArea

from .forms import ContactMessageForm


def home(request):
    areas = PracticeArea.objects.filter(is_active=True)[:4]
    return render(request, "pages/home.html", {"areas": areas, "active_nav": "home"})


def contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you — we've received your message and will call you back shortly.",
            )
            return redirect("pages:contact")
    else:
        form = ContactMessageForm()
    return render(request, "pages/contact.html", {"form": form, "active_nav": "contact"})
