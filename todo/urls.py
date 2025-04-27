from rest_framework_nested import routers
from .views import BlazelyProfileViewSet, TaskViewSet, TaskStepViewSet

router = routers.DefaultRouter()
router.register("profiles", BlazelyProfileViewSet, basename="profile")
router.register("tasks", TaskViewSet, basename="task")

task_router = routers.NestedDefaultRouter(router, "tasks", lookup="task")
task_router.register("steps", TaskStepViewSet, basename="task-step")

urlpatterns = router.urls + task_router.urls
