from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from .views import (
    GoogleLoginView,
    GoogleCallbackView,
    UserViewSet,
    AdminOnlyTokenObtainPairView,
    GoogleIdTokenView,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google_callback"),
    path(
        "google/validate-token/",
        GoogleIdTokenView.as_view(),
        name="validate_google_id_token",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("jwt/create/", AdminOnlyTokenObtainPairView.as_view(), name="token_create"),
    path("jwt/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
] + router.urls
