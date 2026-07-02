from rest_framework.routers import DefaultRouter

from .views import PersonalViewSet

router = DefaultRouter()
router.register("personal", PersonalViewSet, basename="personal")

urlpatterns = router.urls