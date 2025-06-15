from django.db import models
from django.conf import settings


PROFILE_MODEL = settings.PROFILE_MODEL
TASK_LIST_MODEL = settings.TASKLIST_MODEL


class Label(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        PROFILE_MODEL, related_name="labels", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "owner"], name="unique_label")
        ]

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_1 = "1"
    PRIORITY_2 = "2"
    PRIORITY_3 = "3"
    PRIORITY_4 = "4"

    PRIORITY_CHOICES = (
        (PRIORITY_1, "Priority 1"),
        (PRIORITY_2, "Priority 2"),
        (PRIORITY_3, "Priority 3"),
        (PRIORITY_4, "Priority 4"),
    )

    text = models.CharField(max_length=255)
    note = models.CharField(max_length=255, null=True)
    is_completed = models.BooleanField(default=False, db_index=True)
    is_important = models.BooleanField(default=False, db_index=True)
    due_date = models.DateField(null=True, db_index=True)
    reminder_date = models.DateTimeField(null=True)
    priority = models.CharField(
        max_length=1, choices=PRIORITY_CHOICES, default=PRIORITY_4, db_index=True
    )
    label = models.ForeignKey(
        Label, related_name="tasks", on_delete=models.SET_NULL, null=True
    )
    task_list = models.ForeignKey(
        TASK_LIST_MODEL, related_name="tasks", on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        PROFILE_MODEL, related_name="tasks", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class TaskStep(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, related_name="steps", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
