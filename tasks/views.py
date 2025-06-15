from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, TaskStep, Label
from .serializers import TaskSerializer, TaskStepSerializer, LabelSerializer
from .filters import TaskFilter, TaskStepFilter


# Create your views here.
class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        user = self.request.user
        task_list_id = self.kwargs.get("list_pk", None)

        if not task_list_id:
            return (
                Task.objects.prefetch_related("steps")
                .filter(owner__user=user)
                .order_by("created_at")
            )

        return (
            Task.objects.prefetch_related("steps")
            .filter(owner__user=user, task_list=task_list_id)
            .order_by("created_at")
        )

    def get_serializer_context(self):
        return {
            "user_id": self.request.user.id,
            "task_list_id": self.kwargs.get("list_pk", None),
        }

    def create(self, request, *args, **kwargs):
        task_list_id = self.kwargs.get("list_pk", None)

        if not task_list_id:
            return Response(
                {
                    "task_list": "Tasks can only be created via nested endpoints under a list or group. List ID must be passed through the URL."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class TaskStepViewSet(ModelViewSet):
    serializer_class = TaskStepSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskStepFilter

    def get_queryset(self):
        user = self.request.user
        task_id = self.kwargs.get("task_pk", None)

        return TaskStep.objects.filter(task=task_id, task__owner__user=user).order_by(
            "created_at"
        )

    def get_serializer_context(self):
        return {
            "user_id": self.request.user.id,
            "task_id": self.kwargs.get("task_pk", None),
        }


class LabelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LabelSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    def get_queryset(self):
        return Label.objects.filter(owner__user=self.request.user)
