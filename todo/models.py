import uuid
from django.db import models
from django.conf import settings


class BlazelyProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="blazely_profile",
        on_delete=models.CASCADE,
    )
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GroupList(models.Model):
    name = models.CharField(max_length=150)
    archived = models.BooleanField(default=False)
    owner = models.ForeignKey(
        BlazelyProfile, related_name="group_lists", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TaskList(models.Model):
    name = models.CharField(max_length=150)
    group = models.ForeignKey(
        GroupList, related_name="lists", on_delete=models.CASCADE, null=True
    )
    archived = models.BooleanField(default=False)
    owner = models.ForeignKey(
        BlazelyProfile, related_name="lists", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        BlazelyProfile, related_name="labels", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)


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
    note = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False, db_index=True)
    is_important = models.BooleanField(default=False, db_index=True)
    due_date = models.DateField(null=True, db_index=True)
    reminder_date = models.DateField(null=True)
    priority = models.CharField(
        max_length=1, choices=PRIORITY_CHOICES, default=PRIORITY_4, db_index=True
    )
    label = models.ForeignKey(
        Label, related_name="tasks", on_delete=models.SET_NULL, null=True
    )
    task_list = models.ForeignKey(
        TaskList, related_name="tasks", on_delete=models.CASCADE, null=True
    )
    owner = models.ForeignKey(
        BlazelyProfile, related_name="tasks", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.main_text


class TaskStep(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, related_name="steps", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
