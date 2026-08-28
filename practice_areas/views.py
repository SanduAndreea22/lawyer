from django.shortcuts import get_object_or_404, render

from .models import PracticeArea


def practice_area_list(request):
    areas = PracticeArea.objects.filter(is_active=True)
    return render(
        request,
        "practice_areas/list.html",
        {"areas": areas, "active_nav": "practice_areas"},
    )


def practice_area_detail(request, slug):
    area = get_object_or_404(PracticeArea, slug=slug, is_active=True)
    return render(
        request,
        "practice_areas/detail.html",
        {"area": area, "active_nav": "practice_areas"},
    )
