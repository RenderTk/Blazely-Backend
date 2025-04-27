from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import (
    TaskSerializer,
    BlazelyProfileSerializer,
    UpdateBlazelyProfileSerializer,
    TaskStepSerializer,
)
from .models import *


class BlazelyProfileViewSet(ModelViewSet):
    serializer_class = BlazelyProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BlazelyProfile.objects.all()
        return BlazelyProfile.objects.filter(user=self.request.user).select_related(
            "user"
        )

    def get_serializer_class(self):
        method = self.request.method
        if method == "PATCH":
            return UpdateBlazelyProfileSerializer
        return BlazelyProfileSerializer

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
        return Task.objects.filter(owner__user=self.request.user).order_by("created_at")

    def get_serializer_context(self):
        profile = BlazelyProfile.objects.select_related("user").get(
            user=self.request.user
        )
        return {"profile": profile}


class TaskStepViewSet(ModelViewSet):
    serializer_class = TaskStepSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "head", "options"]

    def get_queryset(self):
        task_id = self.kwargs["task_pk"]
        owner = BlazelyProfile.objects.filter(user=self.request.user).first()

        if not Task.objects.filter(pk=task_id).exists():
            return Response(
                {"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not owner:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )

        return TaskStep.objects.filter(task=task_id, task__owner=owner).order_by(
            "created_at"
        )

    def get_serializer_context(self):
        return {"task_id": self.kwargs["task_pk"]}

