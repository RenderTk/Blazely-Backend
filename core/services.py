import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from typing import Dict
from profiles.models import Profile
from .models import GOOGLE_AUTH_PROVIDER
from .models import User

User = get_user_model()


def get_or_create_user(
    email: str, first_name: str = "", last_name: str = "", picture_url: str = None
):

    if email is None:
        raise ValidationError({"email": ["Email is required"]})

    user, created = User.objects.get_or_create(
        email=email,  # Use email to identify users
        auth_provider=GOOGLE_AUTH_PROVIDER,
        defaults={
            "username": email,
            "first_name": first_name or "",
            "last_name": last_name or "",
        },
    )

    if created:
        user.set_unusable_password()
        user.save()
        Profile.objects.create(user=user, profile_picture_url=picture_url)

    return user


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
        "client_id": settings.SOCIAL_AUTH_GOOGLE_WEBCLIENT_ID,  # Google Client ID
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
    user = get_or_create_user(
        email=user_info["email"],
        first_name=user_info.get("given_name", ""),
        last_name=user_info.get("family_name", ""),
        picture_url=user_info.get("picture", None),
    )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
    )


@transaction.atomic
def authenticate_google_id_token(token: str) -> Response:
    """
    Authenticate a user using an ID token from Google.

    Args:
        token: The ID token received from GoogleSignIn.

    Returns:
        A Response object with app-specific JWT tokens or an error.
    """
    try:
        # Validate ID token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.SOCIAL_AUTH_GOOGLE_WEBCLIENT_ID,
        )
        # Verify the issuer (an extra check, though verify_oauth2_token usually covers this)
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValidationError({"error": "Wrong issuer."})

    except requests.exceptions.RequestException as e:
        return Response(
            {"error": "Invalid ID token", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = idinfo.get("email")
    if not email:
        return Response({"error": "Email not available in token"}, status=400)

    user = get_or_create_user(
        email=idinfo["email"],
        first_name=idinfo.get("given_name", ""),
        last_name=idinfo.get("family_name", ""),
        picture_url=idinfo.get("picture", None),
    )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
