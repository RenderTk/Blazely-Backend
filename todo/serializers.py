from .models import *
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

User = get_user_model()


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = ["id", "text"]

    def create(self, validated_data):
        task_id = self.context.get("task_id")
        task = Task.objects.filter(id=task_id).first()
        if not task:
            raise ValidationError("Task is required to create a task step.")

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
        owner = BlazelyProfile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError("Profile is required to create a task.")

        task_list_id = self.context.get("task_list_id")
        task_list = TaskList.objects.filter(id=task_list_id).first()
        if not task_list:
            raise serializers.ValidationError("Task list is required to create a task.")

        validated_data["owner"] = owner
        validated_data["task_list"] = task_list
        return super().create(validated_data)

    def save(self, **kwargs):
        return super().save(**kwargs)


class TaskListSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = TaskList
        fields = ["id", "name", "tasks"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = BlazelyProfile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                "Profile is required to create a task list."
            )
        group_id = self.context.get("group_id")
        group = GroupList.objects.filter(id=group_id).first()
        if group:
            validated_data["group"] = group

        validated_data["owner"] = owner
        return super().create(validated_data)


class GroupListSerializer(serializers.ModelSerializer):
    lists = TaskListSerializer(many=True, read_only=True)

    class Meta:
        model = GroupList
        fields = ["id", "name", "lists"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        profile = BlazelyProfile.objects.filter(user_id=user_id).first()
        if not profile:
            raise serializers.ValidationError(
                "Profile is required to create a group list."
            )

        validated_data["owner"] = profile
        return super().create(validated_data)


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class BlazelyProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    group_lists = GroupListSerializer(many=True, read_only=True)
    lists = serializers.SerializerMethodField(
        method_name="get_lists_without_group", read_only=True
    )

    def get_lists_without_group(self, profile: BlazelyProfile):
        # Check if ungrouped_lists already exists on the profile instance
        if hasattr(profile, "ungrouped_lists"):
            ungrouped_lists = profile.ungrouped_lists
        else:
            # Only query if the lists weren't prefetched
            queryset = BlazelyProfile.objects.prefetch_related(
                Prefetch(
                    "lists",
                    queryset=TaskList.objects.filter(group=None).prefetch_related(
                        "tasks__steps"
                    ),
                    to_attr="ungrouped_lists",
                )
            ).get(id=profile.id)
            ungrouped_lists = queryset.ungrouped_lists

        return TaskListSerializer(ungrouped_lists, many=True).data

    class Meta:
        model = BlazelyProfile
        fields = [
            "id",
            "birth_date",
            "user",
            "profile_picture_url",
            "lists",
            "group_lists",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        user = self.context.get("user")
        if not user:
            raise ValidationError("User is required to create a profile.")

        if BlazelyProfile.objects.filter(user=user).exists():
            raise ValidationError("User already has a profile.")

        validated_data["user"] = user
        return super().create(validated_data)


class BlazelyProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlazelyProfile
        fields = ["birth_date"]
