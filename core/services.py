import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from typing import Dict, Optional
from .models import GOOGLE_AUTH_PROVIDER
from .models import User

User = get_user_model()


@transaction.atomic
def authenticate_google_user(code: str) -> Response:
    """
    Authenticate a user using Google OAuth2.

    Args:
        code: A string representing the authorization code from Google.

    Returns:
        A Response object with a JSON payload. The payload will contain
        the access and refresh tokens on success, or an error message and
        HTTP status on failure.
    """
    token_url = "https://oauth2.googleapis.com/token"
    data: Dict[str, str] = {
        "code": code,  # The authorization code from Google
        "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,  # Google Client ID
        "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,  # Google Client Secret
        "redirect_uri": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI,  # The redirect URI
        "grant_type": "authorization_code",
    }
    try:
        token_response = requests.post(token_url, data=data)
        token_response.raise_for_status()  # Ensure request was successful
        tokens = token_response.json()  # Convert response to JSON
    except requests.exceptions.RequestException as e:
        return Response(
            {"error": "Could not retrieve tokens", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers: Dict[str, str] = {"Authorization": f"Bearer {tokens.get('access_token')}"}  # type: ignore
    try:
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
    except requests.exceptions.RequestException as e:
        return Response(
            {"error": "Could not retrieve user info", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user, created = User.objects.get_or_create(
        email=user_info["email"],  # Use email to identify users
        auth_provider=GOOGLE_AUTH_PROVIDER,
        defaults={
            "username": user_info.get("email"),  # Set username as email
            "first_name": user_info.get("given_name", ""),  # Get first name
            "last_name": user_info.get("family_name", ""),  # Get last name
        },
    )
    user.set_unusable_password()
    user.save()
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "message": "Login successful!",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
    )
