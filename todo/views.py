from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import BlazelyProfileSerializer, UpdateBlazelyProfileSerializer
from .models import *


class BlazelyProfileViewSet(ModelViewSet):
    serializer_class = BlazelyProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if self.request.user.is_active is False:
            return Response(
                {"error": "User is not active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


