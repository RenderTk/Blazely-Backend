from django.db import models
from django.conf import settings

PROFILE_MODEL = settings.PROFILE_MODEL


# Create your models here.
class GroupList(models.Model):
    name = models.CharField(max_length=150)
    archived = models.BooleanField(default=False)
    owner = models.ForeignKey(
        PROFILE_MODEL, related_name="group_lists", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "owner"], name="unique_group_list")
        ]