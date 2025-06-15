from django.utils.module_loading import import_string
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from .models import TaskList
from .serializers import TaskListSerializer, TaskListWithoutGroupSerializer
from .filters import TaskListFilter

# Custom permissions
IsSuperUser: BasePermission = import_string("core.permisions.IsSuperUser")


# Create your views here.
class TaskListViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskListFilter

    def get_queryset(self):
        user = self.request.user
        group_id = self.kwargs.get("group_pk", None)

        if user.is_superuser:
            if group_id:
                return (
                    TaskList.objects.prefetch_related("tasks__steps")
                    .filter(group_id=group_id)
                    .order_by("created_at")
                )

            return TaskList.objects.prefetch_related("tasks__steps").order_by(
                "created_at"
            )
        else:
            # if group_id was provided by url
            if group_id:
                return (
                    TaskList.objects.prefetch_related("tasks__steps")
                    .filter(owner__user=user, group_id=group_id)
                    .order_by("created_at")
                )

            # if group_id was not provided
            return (
                TaskList.objects.prefetch_related("tasks__steps")
                .filter(owner__user=user)
                .order_by("created_at")
            )

    def get_serializer_class(self):
        group_id = self.kwargs.get("group_pk", None)
        if group_id:
            return TaskListWithoutGroupSerializer
        return TaskListSerializer

    def get_serializer_context(self):
        # if group_id was not provided in the url
        # validation will be done in the serializer
        return {
            "user_id": self.request.user.id,
            "group_id": self.kwargs.get("group_pk", None),
        }
