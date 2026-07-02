from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponseForbidden
from django.views.static import serve


def protected_media(request, path):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Authentication required')
    return serve(request, path, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('pacientes.urls')),
    path('api/', include('personal.urls')),
    path('api/', include('colonoscopia.urls')),
    path('api/', include('eda.urls')),
    path('api/', include('imagenes.urls')),
    path('api/procedimientos/', include('procedimientos.urls')),
    path('reportes/', include('reportes.urls')),
    path('api-auth/', include('rest_framework.urls')),  # login/logout para la API navegable
]

if settings.DEBUG:
    urlpatterns += [path('media/<path:path>', protected_media)]