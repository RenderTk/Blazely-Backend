from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import SAFE_METHODS
from .models import Profile
from .serializers import ProfileSerializer, ProfileUpdateSerializer

# Custom permissions
IsSuperUser: BasePermission = import_string("core.permisions.IsSuperUser")


# Create your views here.
class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        if self.action == "list":
            return [IsSuperUser()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Profile.objects.all()
        return (
            Profile.objects.prefetch_related("group_lists__lists__tasks__steps")
            .filter(user=self.request.user)
            .select_related("user")
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ProfileSerializer
        return ProfileUpdateSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        user = self.request.user
        profile = get_object_or_404(Profile, user=user)
        return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)
