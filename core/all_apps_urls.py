from rest_framework_nested import routers
from profiles.urls import router as profiles_router
from grouplists.urls import router as group_router
from tasklists.urls import router as list_router
from tasks.urls import router as task_router
from tasks.views import TaskViewSet, TaskStepViewSet
from tasklists.views import TaskListViewSet
from .urls import router as core_router

router = routers.DefaultRouter()
for r in profiles_router.registry:
    router.registry.append(r)

for r in group_router.registry:
    router.registry.append(r)

for r in list_router.registry:
    router.registry.append(r)

for r in task_router.registry:
    router.registry.append(r)

# for r in core_router.registry:
#     router.registry.append(r)


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


task_step_router = routers.NestedDefaultRouter(router, "tasks", lookup="task")
task_step_router.register("steps", TaskStepViewSet, basename="task-step")




# Combine all URLs
urlpatterns = (
    router.urls
    + group_router.urls
    + list_router.urls
    + group_list_router.urls
    + list_task_router.urls
    + group_list_task_router.urls
    + task_step_router.urls
)
