from rest_framework_nested import routers
from . import views

# Main router
router = routers.DefaultRouter()
router.register("lists", views.TaskListViewSet, basename="list")