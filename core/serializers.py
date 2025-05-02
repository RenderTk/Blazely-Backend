from django.db import transaction
from rest_framework import serializers
from todo.models import BlazelyProfile
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        min_length=2,
    )
    last_name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        min_length=2,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "username",
            "is_staff",
            "is_superuser",
        ]

    @transaction.atomic
    def create(self, validated_data):
        user = super().create(validated_data)
        BlazelyProfile.objects.create(user=user)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        min_length=2,
    )
    last_name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        min_length=2,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
        ]


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
        ]


class UserActivationSerializer(serializers.Serializer):
    def save(self, **kwargs):
        action = self.context.get("action")
        if not action:
            raise serializers.ValidationError(
                "Action is required. (activate or deactivate)"
            )

        if action not in ["activate", "deactivate"]:
            raise serializers.ValidationError(
                "Invalid action. (Valid actions: activate or deactivate)"
            )

        if action == "activate":
            self.instance.is_active = True

        elif action == "deactivate":
            self.instance.is_active = False

        self.instance.save()
