from .models import *
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
import emoji

User = get_user_model()


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = ["id", "text"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = BlazelyProfile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a task."}
            )

        task_id = self.context.get("task_id")
        task = Task.objects.filter(id=task_id, owner=owner).first()
        if not task:
            raise ValidationError({"task": "Task is required to create a step."})

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


class TaskListSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = TaskList
        fields = [
            "id",
            "name",
            "emoji",
            "group",
            "tasks",
        ]

    def validate_emoji(self, value):
        if not emoji.is_emoji(value):
            raise ValidationError({"emoji": "Invalid emoji."})
        return value

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = BlazelyProfile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a task list."}
            )
        if TaskList.objects.filter(name=validated_data["name"], owner=owner).exists():
            raise serializers.ValidationError(
                {"name": "List with given name already exists."}
            )
        validated_data["owner"] = owner
        return super().create(validated_data)


class TaskListWithoutGroupSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    def validate_emoji(self, value):
        if not emoji.is_emoji(value):
            raise ValidationError({"emoji": "Invalid emoji."})
        return value

    class Meta:
        model = TaskList
        fields = ["id", "name", "emoji", "tasks"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = BlazelyProfile.objects.filter(user_id=user_id).first()
        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a task list."}
            )
        if TaskList.objects.filter(name=validated_data["name"], owner=owner).exists():
            raise serializers.ValidationError(
                {"name": "List with given name already exists."}
            )

        group_id = self.context.get("group_id")
        group = GroupList.objects.filter(id=group_id, owner=owner).first()
        if group:
            validated_data["group"] = group

        validated_data["owner"] = owner
        return super().create(validated_data)


class GroupListSerializer(serializers.ModelSerializer):
    lists = TaskListWithoutGroupSerializer(many=True, read_only=True)

    class Meta:
        model = GroupList
        fields = ["id", "name", "lists"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        owner = BlazelyProfile.objects.filter(user_id=user_id).first()
        if GroupList.objects.filter(name=validated_data["name"], owner=owner).exists():
            raise serializers.ValidationError(
                {"name": "Group list with given name already exists."}
            )

        if not owner:
            raise serializers.ValidationError(
                {"owner": "Profile is required to create a group list."}
            )

        validated_data["owner"] = owner
        return super().create(validated_data)


class ManageListsOnGroupSerializer(serializers.Serializer):
    tasklist_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
        allow_null=False,
    )

    def validate_tasklist_ids(self, value):
        action = self.context.get("action")
        group_list = self.context.get("group_list")

        if action == "add":
            valid_tasklists = TaskList.objects.filter(id__in=value).exclude(
                group=group_list
            )
            error_msg = "already assigned to this group"
        elif action == "remove":
            valid_tasklists = TaskList.objects.filter(id__in=value, group=group_list)
            error_msg = "not assigned to this group"

        if not valid_tasklists.exists():
            raise serializers.ValidationError(
                {
                    "tasklist_ids": f"No valid tasklists found for this action - they may be {error_msg}."
                }
            )

        return value

    def save(self, **kwargs):
        action = self.context.get("action")
        group = self.context.get("group_list")

        if action not in ["add", "remove"]:
            raise serializers.ValidationError(
                {"action": "Invalid or missing action. Expected 'add' or 'remove'."}
            )

        tasklist_ids = self.validated_data.get("tasklist_ids", [])

        with transaction.atomic():
            # Your existing save logic here
            if action == "add":
                TaskList.objects.filter(id__in=tasklist_ids).update(group=group)
            elif action == "remove":
                TaskList.objects.filter(id__in=tasklist_ids).update(group=None)

        return group


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class BlazelyProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = BlazelyProfile
        fields = [
            "id",
            "birth_date",
            "user",
            "profile_picture_url",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        user = self.context.get("user")
        if not user:
            raise ValidationError({"user": "User is required to create a profile."})

        if BlazelyProfile.objects.filter(user=user).exists():
            raise ValidationError("User already has a profile.")

        validated_data["user"] = user
        return super().create(validated_data)


class BlazelyProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlazelyProfile
        fields = ["birth_date"]
