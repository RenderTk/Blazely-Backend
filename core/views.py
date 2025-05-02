from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserActivationSerializer,
)
from .services import authenticate_google_user

User = get_user_model()


class UserViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]

        if self.action == "activate" or self.action == "deactivate":
            return [IsAdminUser()]

        elif self.request.method == "POST":
            return [IsAdminUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == "activate" or self.action == "deactivate":
            return UserActivationSerializer

        if self.request.method == "POST":
            return UserCreateSerializer
        elif self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        if request.method == "PATCH":
            serializer = UserUpdateSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def activate(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if user.is_active:
            return Response(
                {"error": "User is already active"}, status=status.HTTP_400_BAD_REQUEST
            )
        serialzier = UserActivationSerializer(
            user, data=request.data, context={"action": "activate"}
        )
        serialzier.is_valid(raise_exception=True)
        serialzier.save()
        return Response(
            {"message": "User activated successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["patch"])
    def deactivate(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if not user.is_active:
            return Response(
                {"error": "User is already inactive"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serialzier = UserActivationSerializer(
            user, data=request.data, context={"action": "deactivate"}
        )
        serialzier.is_valid(raise_exception=True)
        serialzier.save()
        return Response(
            {"message": "User deactivated successfully."}, status=status.HTTP_200_OK
        )


class AdminOnlyTokenObtainPairView(APIView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request):
        # First get the username/email from the request
        username_field = User.USERNAME_FIELD
        username = request.data.get(username_field)

        # Pre-check if the user is staff before validating credentials
        try:
            user = User.objects.get(**{username_field: username})
            if not user.is_staff and not user.is_superuser:
                # Return the same error but don't validate credentials
                return Response(
                    {
                        "error": "Email and password authentication is not allowed for this user."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        except User.DoesNotExist:
            pass

        try:
            # Now validate credentials
            serializer = TokenObtainPairSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # If we reach here, the user exists, is staff or superuser, and credentials are valid
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class GoogleLoginView(APIView):
    """Endpoint to generate Google OAuth login URL."""

    def get(self, request):
        # Define the redirect URI (localhost)
        redirect_uri = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI
        login_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}&"
            f"response_type=code&"
            f"redirect_uri={redirect_uri}&"
            f"scope=email%20profile"
        )
        return Response({"login_url": login_url}, status=status.HTTP_200_OK)


class GoogleCallbackView(APIView):
    """View to handle Google OAuth callback"""

    def get(self, request):
        # Extract the authorization code from the request body
        code = request.query_params.get("code")
        # Validate that a code is provided
        if not code:
            return Response(
                {"error": "No authorization code provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Authenticate the user with the provided authorization code
        return authenticate_google_user(code)
