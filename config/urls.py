from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('pacientes.urls')),
    path('api/', include('personal.urls')),
    path('api/', include('colonoscopia.urls')),
    path('api/', include('eda.urls')),
    path('api/', include('imagenes.urls')),
    path('reportes/', include('reportes.urls')),
    path('api-auth/', include('rest_framework.urls')),  # login/logout para la API navegable
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)