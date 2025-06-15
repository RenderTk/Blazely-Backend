from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import (
    UserCreateSerializer,
    SuperUserSerializer,
    SimpleUserSerializer,
    UserUpdateSerializer,
    SuperUserUpdateSerializer,
    UserActivationSerializer,
)
from .permisions import IsSuperUser
from .services import authenticate_google_user, authenticate_google_id_token

User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = [IsSuperUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == "activate" or self.action == "deactivate":
            return UserActivationSerializer

        if self.request.method == "POST":
            return UserCreateSerializer

        elif self.request.method == "PATCH":

            if self.request.user.is_superuser:
                return SuperUserUpdateSerializer

            return UserUpdateSerializer

        if self.request.method == "GET":
            if self.request.user.is_superuser:
                return SuperUserSerializer

            return SimpleUserSerializer

    @action(
        detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user

        if request.method == "PATCH":
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if user.is_superuser:
            data = SuperUserSerializer(user).data
        else:
            data = SimpleUserSerializer(user).data

        return Response(data, status=status.HTTP_200_OK)

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


class SuperUserOnlyTokenObtainPairView(APIView):
    """
    Token endpoint restricted to superusers only.
    Regular users should use Google OAuth for authentication.
    """

    serializer_class = TokenObtainPairSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = serializer.user
        if not user.is_superuser:
            # Credentials are correct, but not a superuser — return 403
            return Response(
                {"detail": "Not authorized."},  # Generic message
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    """Endpoint to generate Google OAuth login URL."""

    def get(self, request):
        # Define the redirect URI (localhost)
        redirect_uri = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI
        login_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.SOCIAL_AUTH_GOOGLE_WEBCLIENT_ID}&"
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


class GoogleIdTokenView(APIView):
    """View to handle Google ID token validation"""

    def post(self, request):
        # Extract the ID token from the request body
        id_token = request.data.get("id_token")
        # Validate that an ID token is provided
        if not id_token:
            return Response(
                {"error": "No ID token provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Authenticate the user with the provided ID token
        return authenticate_google_id_token(id_token)
