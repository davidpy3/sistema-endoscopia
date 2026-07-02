from rest_framework.routers import DefaultRouter

from .views import ImagenEndoscopicaViewSet

router = DefaultRouter()
router.register("imagenes", ImagenEndoscopicaViewSet, basename="imagen")

urlpatterns = router.urls