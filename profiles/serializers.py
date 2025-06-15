from django.db.models import Model
from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers
from .models import Profile


# Serializers
SimpleUserSerializer: serializers.ModelSerializer = import_string(
    settings.SIMPLE_USER_SERIALIZER
)

class ProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Profile
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
            raise serializers.ValidationError({"user": "User is required to create a profile."})

        if Profile.objects.filter(user=user).exists():
            raise serializers.ValidationError("User already has a profile.")

        validated_data["user"] = user
        return super().create(validated_data)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["birth_date"]