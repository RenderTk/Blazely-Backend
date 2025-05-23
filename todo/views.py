from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .models import *
from .filters import *


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


class TaskListViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskListFilter

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


class GroupListViewSet(ModelViewSet):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GroupListFilter

    def get_queryset(self):
        user = self.request.user

        return (
            GroupList.objects.prefetch_related("lists__tasks__steps")
            .filter(owner__user=user)
            .order_by("created_at")
        )

    def get_serializer_class(self):
        if self.action == "manage_lists":
            return ManageListsOnGroupSerializer
        return GroupListSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    @action(detail=True, methods=["patch"])
    def manage_lists(self, request, pk=None):
        action = self.request.query_params.get("action", None)
        if action not in ["add", "remove"]:
            return Response(
                {"action": "Invalid or missing action. Expected 'add' or 'remove'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # gets the group object in the url and validates if it exists
        # and if the user is the owner
        group_list: GroupList = self.get_object()

        serializer = ManageListsOnGroupSerializer(
            data=request.data, context={"group_list": group_list, "action": action}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": f"Lists successfully {'added' if action == 'add' else 'removed'}"
            },
            status=status.HTTP_200_OK,
        )
