from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, basename="user")

urlpatterns = [
    path("google/login/", views.GoogleLoginView.as_view(), name="google_login"),
    path(
        "google/callback/", views.GoogleCallbackView.as_view(), name="google_callback"
    ),
    path(
        "google/validate-token/",
        views.GoogleIdTokenView.as_view(),
        name="validate_google_id_token",
    ),
    path(
        "jwt/create/",
        views.SuperUserOnlyTokenObtainPairView.as_view(),
        name="token_create",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("jwt/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
] + router.urls
