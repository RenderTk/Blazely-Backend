from django.db import models
from django.contrib.auth.models import AbstractUser

GOOGLE_AUTH_PROVIDER = "google"
APPLE_AUTH_PROVIDER = "apple"
EMAIL_AUTH_PROVIDER = "django"
AUTH_PROVIDERS = [
    (GOOGLE_AUTH_PROVIDER, "Google"),
    (APPLE_AUTH_PROVIDER, "Apple"),
    (EMAIL_AUTH_PROVIDER, "Email/Password"),
]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    auth_provider = models.CharField(
        max_length=30,
        choices=AUTH_PROVIDERS,
        default=EMAIL_AUTH_PROVIDER,
        db_index=True,
    )

    class Meta(AbstractUser.Meta):
        pass
