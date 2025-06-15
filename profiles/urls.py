from rest_framework_nested import routers
from . import views

# Main router
router = routers.DefaultRouter()
router.register("profiles", views.ProfileViewSet, basename="profile")