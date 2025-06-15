from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from profiles.models import Profile
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
        Profile.objects.create(user=user)
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


class SuperUserUpdateSerializer(serializers.ModelSerializer):
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

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "username",
            "password",
        ]

    def update(self, instance, validated_data):
        password = validated_data.get("password", None)

        # If password is provided, update it to the hashed version
        if password:
            validated_data["password"] = make_password(password)

        return super().update(instance, validated_data)


class SuperUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "is_staff",
            "is_superuser",
            "is_active",
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


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
