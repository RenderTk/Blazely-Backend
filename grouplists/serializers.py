from django.db.models import Model
from django.db import transaction
from django.conf import settings
from django.apps import apps
from django.utils.module_loading import import_string
from rest_framework import serializers
from .models import GroupList

# Models
Profile: Model = apps.get_model(settings.PROFILE_MODEL)
TaskList: Model = apps.get_model(settings.TASKLIST_MODEL)

# Serializers
TaskListWithoutGroupSerializer: serializers.ModelSerializer = import_string(
    settings.TASKLIST_WITHOUT_GROUP_SERIALIZER
)


class GroupListSerializer(serializers.ModelSerializer):
    lists = TaskListWithoutGroupSerializer(many=True, read_only=True)

    class Meta:
        model = GroupList
        fields = ["id", "name", "lists"]

    def create(self, validated_data):
        user = self.context.get("user")
        owner = Profile.objects.filter(user=user).first()
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
