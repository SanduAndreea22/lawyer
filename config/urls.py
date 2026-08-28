from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("practice-areas/", include("practice_areas.urls")),
    path("team/", include("team.urls")),
    path("booking/", include("booking.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # No object storage (S3/Cloudinary) is wired up yet, and Django's static()
    # helper above only serves media in DEBUG mode - without this, lawyer
    # photos and uploaded case documents would 404 in any real deployment.
    # Serving media through Django like this is fine for a small, low-traffic
    # deployment; swap in django-storages + S3 (or similar) before there's
    # meaningful traffic, and note that anyone with a media URL can currently
    # fetch it directly with no login check.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve_static,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
