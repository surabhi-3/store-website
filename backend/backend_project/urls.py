from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),                      # Django admin
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout
    path("", include("store.urls")),                      # all store + api routes
]


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)