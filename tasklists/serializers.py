import emoji
from django.db.models import Model
from django.conf import settings
from django.apps import apps
from django.utils.module_loading import import_string
from rest_framework import serializers

# Models
Profile: Model = apps.get_model(settings.PROFILE_MODEL)
TaskList: Model = apps.get_model(settings.TASKLIST_MODEL)
GroupList: Model = apps.get_model(settings.GROUP_LIST_MODEL)

# Serializers
TaskSerializer: serializers.ModelSerializer = import_string(settings.TASK_SERIALIZER)


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
            raise serializers.ValidationError({"emoji": "Invalid emoji."})
        return value

    def create(self, validated_data):
        user = self.context.get("user")
        owner = Profile.objects.filter(user=user).first()
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
            raise serializers.ValidationError({"emoji": "Invalid emoji."})
        return value

    class Meta:
        model = TaskList
        fields = ["id", "name", "emoji", "tasks"]

    def create(self, validated_data):
        user = self.context.get("user")
        owner = Profile.objects.filter(user=user).first()
        if not owner:
            raise serializers.serializers.ValidationError(
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
