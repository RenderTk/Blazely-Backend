from .models import *
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class BlazelyProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = BlazelyProfile
        fields = ["id", "birth_date", "user"]

    def create(self, validated_data):
        user = self.context.get("user")
        if not user:
            raise ValidationError("User is required to create a profile.")

        if BlazelyProfile.objects.filter(user=user).exists():
            raise ValidationError("User already has a profile.")

        validated_data["user"] = user
        return super().create(validated_data)


class UpdateBlazelyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlazelyProfile
        fields = ["birth_date"]


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = ["id", "text"]

    def create(self, validated_data):
        task_id = self.context.get("task_id")
        if not task_id:
            raise ValidationError("Task is required to create a task step.")

        validated_data["task_id"] = task_id
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
            "task_list",
            "owner",
            "steps",
        ]
        read_only_fields = ["owner"]

    def create(self, validated_data):
        profile = self.context.get("profile")
        if not profile:
            raise serializers.ValidationError("Profile is required to create a task.")

        validated_data["owner"] = profile
        return super().create(validated_data)

    def save(self, **kwargs):
        return super().save(**kwargs)
