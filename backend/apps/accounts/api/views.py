from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from core.utils import success_response, error_response
from apps.accounts.api.serializers import (
    RegisterSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
)


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error="ValidationError",
                message="Registration failed.",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            message="Account created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        from django.contrib.auth import authenticate

        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password", "")

        if not email or not password:
            return error_response(
                error="ValidationError",
                message="Email and password are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return error_response(
                error="AuthenticationFailed",
                message="Invalid email or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return error_response(
                error="AccountDisabled",
                message="This account has been disabled.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            message="Login successful.",
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return error_response(
                error="ValidationError",
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return error_response(
                error="TokenError",
                message="Invalid or already expired refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return success_response(message="Logged out successfully.")


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return success_response(data=UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if not serializer.is_valid():
            return error_response(
                error="ValidationError",
                message="Profile update failed.",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        return success_response(
            data=UserSerializer(user).data,
            message="Profile updated successfully.",
        )


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error_response(
                error="ValidationError",
                message="Password change failed.",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return success_response(message="Password changed successfully.")
