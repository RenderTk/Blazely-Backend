import uuid
from django.db import models
from django.conf import settings

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    birth_date = models.DateField(null=True, blank=True)
    profile_picture_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)