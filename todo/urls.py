from rest_framework_nested import routers
from .views import BlazelyProfileViewSet

router = routers.DefaultRouter()
router.register("profile", BlazelyProfileViewSet, basename="profile")

urlpatterns = router.urls
