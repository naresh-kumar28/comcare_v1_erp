from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from drf_spectacular.utils import extend_schema

from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Registers a new user with email, password, and profile details.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        profile_data = ProfileSerializer(user, context={'request': request}).data

        return Response({
            'success': True,
            'message': 'Registration successful.',
            'user': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    POST /api/v1/auth/login/
    Authenticates user with email and password. Returns JWT tokens & profile.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        profile_data = ProfileSerializer(user, context={'request': request}).data

        return Response({
            'success': True,
            'message': 'Login successful.',
            'user': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklists the given refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=LogoutSerializer)
    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Successfully logged out.'
        }, status=status.HTTP_200_OK)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/auth/me/
    PATCH /api/v1/auth/me/
    Retrieves or updates the authenticated user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class PasswordChangeAPIView(APIView):
    """
    POST /api/v1/auth/password/change/
    Allows authenticated users to change their password.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=PasswordChangeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'success': True,
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    """
    POST /api/v1/auth/password/reset/
    Generates password reset credentials for a registered user.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=PasswordResetSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return Response({
                'success': True,
                'message': 'If an account exists with this email, a password reset token has been generated.',
                'uid': uid,
                'token': token
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'success': True,
                'message': 'If an account exists with this email, a password reset token has been generated.'
            }, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    """
    POST /api/v1/auth/password/reset/confirm/
    Resets password using valid UID, token, and new password.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=PasswordResetConfirmSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)
