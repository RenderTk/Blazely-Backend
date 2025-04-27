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
        user = self.context["request"].user
        if BlazelyProfile.objects.filter(user=user).exists():
            raise ValidationError("User already has a profile")

        return BlazelyProfile.objects.create(user=user, **validated_data)


class UpdateBlazelyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlazelyProfile
        fields = ["birth_date"]
