from django.shortcuts import render

from .models import Lawyer


def team_list(request):
    lawyers = Lawyer.objects.filter(is_active=True).prefetch_related("practice_areas")
    return render(request, "team/list.html", {"lawyers": lawyers, "active_nav": "team"})
