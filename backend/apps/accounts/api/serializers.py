from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.accounts.models import User, UserProfile, College


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ("id", "name", "code")
        read_only_fields = ("id",)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ("avatar", "bio", "total_points", "total_stars", "streak_days", "last_active")
        read_only_fields = ("total_points", "total_stars", "streak_days")


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    college_detail = CollegeSerializer(source="college", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "mobile",
            "role",
            "is_college_student",
            "college",
            "college_detail",
            "college_name",
            "branch",
            "current_year",
            "semester",
            "cgpa",
            "roll_number",
            "profile",
            "created_at",
        )
        read_only_fields = ("id", "email", "role", "created_at")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "mobile",
            "password",
            "password2",
            "is_college_student",
            "college_name",
            "branch",
            "current_year",
            "semester",
            "roll_number",
        )

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value: str) -> str:
        user: User = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Handles both User field updates and nested profile updates."""

    bio = serializers.CharField(source="profile.bio", allow_blank=True, required=False)
    avatar = serializers.ImageField(source="profile.avatar", required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "mobile",
            "is_college_student",
            "college",
            "college_name",
            "branch",
            "current_year",
            "semester",
            "cgpa",
            "roll_number",
            "bio",
            "avatar",
        )

    def update(self, instance: User, validated_data: dict) -> User:
        profile_data = validated_data.pop("profile", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
