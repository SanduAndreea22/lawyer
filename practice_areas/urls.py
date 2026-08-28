from django.urls import path

from . import views

app_name = "practice_areas"

urlpatterns = [
    path("", views.practice_area_list, name="list"),
    path("<slug:slug>/", views.practice_area_detail, name="detail"),
]
