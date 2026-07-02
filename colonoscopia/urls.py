from rest_framework.routers import DefaultRouter

from .views import ColonoscopiaViewSet

router = DefaultRouter()
router.register("colonoscopias", ColonoscopiaViewSet, basename="colonoscopia")

urlpatterns = router.urls