from rest_framework_nested import routers
from .views import (
    BlazelyProfileViewSet,
    TaskViewSet,
    TaskStepViewSet,
    TaskListViewSet,
    GroupListViewSet,
)

# Main router
router = routers.DefaultRouter()
router.register("profiles", BlazelyProfileViewSet, basename="profile")
router.register("lists", TaskListViewSet, basename="list")
router.register("groups", GroupListViewSet, basename="group")

# Group -> Lists nesting
group_router = routers.NestedDefaultRouter(router, "groups", lookup="group")
group_router.register("lists", TaskListViewSet, basename="group-list")

# Group -> Lists -> Tasks nesting
group_list_router = routers.NestedDefaultRouter(group_router, "lists", lookup="list")
group_list_router.register("tasks", TaskViewSet, basename="group-list-task")

# Group -> Lists -> Tasks -> Steps nesting
group_list_task_router = routers.NestedDefaultRouter(
    group_list_router, "tasks", lookup="task"
)
group_list_task_router.register(
    "steps", TaskStepViewSet, basename="group-list-task-step"
)

# Lists -> Tasks nesting
list_router = routers.NestedDefaultRouter(router, "lists", lookup="list")
list_router.register(
    "tasks", TaskViewSet, basename="list-task"
)  # Note: Changed to TaskViewSet


# Lists -> Tasks -> Steps nesting
list_task_router = routers.NestedDefaultRouter(list_router, "tasks", lookup="task")
list_task_router.register("steps", TaskStepViewSet, basename="list-task-step")


# Combine all URLs
urlpatterns = (
    router.urls
    + group_router.urls
    + list_router.urls
    + group_list_router.urls
    + list_task_router.urls
    + group_list_task_router.urls
)
