from django.urls import path
from .views import GoogleLoginView, GoogleCallbackView

urlpatterns = [
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google_callback"),
]
