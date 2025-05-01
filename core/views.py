from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import authenticate_google_user


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
