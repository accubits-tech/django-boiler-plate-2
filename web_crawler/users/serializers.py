from django.contrib.auth import get_user_model
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "username",
        )


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = ("username", "password")


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)
    department = serializers.CharField(max_length=300)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "username",
            "department",
        )


class ForgotPasswordSerializer(serializers.Serializer):
    pass


class ResetPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=200)
    token = serializers.CharField(max_length=1000)


class RefreshTokenSerializer(serializers.Serializer):

    refresh_token = serializers.CharField(max_length=1000)

class ImageSerializer(serializers.Serializer):
    pass


class UserSearchSerializer(serializers.Serializer):

    search_value = serializers.CharField(max_length=200)
    search_count = serializers.IntegerField(default=0)
    search_result_id = serializers.CharField(max_length=100)


class UserBookmarkSerializer(serializers.Serializer):
    content_id = serializers.IntegerField()
    content_text = serializers.CharField(max_length=200)
    content_url = serializers.CharField(max_length=200)


class MonitorySerializer(serializers.Serializer):

    search_value_id = serializers.CharField()


class UserNotesSerializer(serializers.Serializer):
    note_text = serializers.CharField()
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class UserNotificationsSerializer(serializers.Serializer):
    notification_text = serializers.CharField()
    created_at = serializers.DateTimeField()


class DashboardSerializer(serializers.Serializer):
    pass
