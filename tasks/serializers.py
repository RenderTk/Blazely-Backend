from django.db.models import Model
from django.apps import apps
from django.conf import settings
from rest_framework import serializers
from .models import Task, TaskStep, Label


# Models
Profile: Model = apps.get_model(settings.PROFILE_MODEL)
TaskList: Model = apps.get_model(settings.TASKLIST_MODEL)


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = ["id", "text"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = Profile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a task."}
            )

        task_id = self.context.get("task_id")
        task = Task.objects.filter(id=task_id, owner=owner).first()
        if not task:
            raise serializers.ValidationError(
                {"task": "Task is required to create a step."}
            )

        validated_data["task"] = task
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    steps = TaskStepSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "text",
            "note",
            "is_completed",
            "is_important",
            "due_date",
            "reminder_date",
            "priority",
            "label",
            "steps",
        ]
        read_only_fields = ["owner"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = Profile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a task."}
            )

        task_list_id = self.context.get("task_list_id")
        task_list = TaskList.objects.filter(id=task_list_id, owner=owner).first()
        if not task_list:
            raise serializers.ValidationError(
                {"task_list": "Task list is required to create a task."}
            )

        validated_data["owner"] = owner
        validated_data["task_list"] = task_list
        return super().create(validated_data)

    def save(self, **kwargs):
        return super().save(**kwargs)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["name"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        if not user_id:
            raise serializers.ValidationError(
                {"user_id": "User ID is required to create a label."}
            )

        owner = Profile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a label."}
            )
        validated_data["owner"] = owner

        return super().create(validated_data)
