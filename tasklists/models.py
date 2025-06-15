from django.db import models
from django.conf import settings


PROFILE_MODEL = settings.PROFILE_MODEL
GROUP_LIST_MODEL = settings.GROUP_LIST_MODEL

# Create your models here.
class TaskList(models.Model):
    name = models.CharField(max_length=150)
    group = models.ForeignKey(
        GROUP_LIST_MODEL, related_name="lists", on_delete=models.CASCADE, null=True
    )
    archived = models.BooleanField(default=False)
    owner = models.ForeignKey(
        PROFILE_MODEL, related_name="lists", on_delete=models.CASCADE
    )
    emoji = models.CharField(max_length=100, null=True, default="📃")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "owner"], name="unique_task_list")
        ]