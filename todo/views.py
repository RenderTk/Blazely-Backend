from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *


class BlazelyProfileViewSet(ModelViewSet):
    serializer_class = BlazelyProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return BlazelyProfile.objects.all()
        return (
            BlazelyProfile.objects.prefetch_related("group_lists__lists__tasks__steps")
            .filter(user=self.request.user)
            .select_related("user")
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BlazelyProfileSerializer
        return BlazelyProfileUpdateSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        user = self.request.user
        profile = get_object_or_404(BlazelyProfile, user=user)
        return Response(
            BlazelyProfileSerializer(profile).data, status=status.HTTP_200_OK
        )


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        task_list_id = self.kwargs["list_pk"]

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


class TaskStepViewSet(ModelViewSet):
    serializer_class = TaskStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        task_id = self.kwargs.get("task_pk", None)

        return TaskStep.objects.filter(task=task_id, task__owner__user=user).order_by(
            "created_at"
        )

    def get_serializer_context(self):
        return {"task_id": self.kwargs.get("task_pk", None)}


class TaskListViewSet(ModelViewSet):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        group_id = self.kwargs.get("group_pk", None)

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

    def get_serializer_context(self):
        # if group_id was not provided in the url
        # validation will be done in the serializer
        return {
            "user_id": self.request.user.id,
            "group_id": self.kwargs.get("group_pk", None),
        }


class GroupListViewSet(ModelViewSet):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return (
            GroupList.objects.prefetch_related("lists__tasks__steps")
            .filter(owner__user=user)
            .order_by("created_at")
        )

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}
