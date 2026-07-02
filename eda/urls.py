from rest_framework.routers import DefaultRouter

from .views import EDAViewSet

router = DefaultRouter()
router.register("edas", EDAViewSet, basename="eda")

urlpatterns = router.urls