from django.contrib.auth import views as auth_views

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('schedule/', include('schedule.urls')),
    path('appointments/', include('appointments.urls')),
    path('payments/', include('payments.urls')),

    path('select2/', include('django_select2.urls')),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
