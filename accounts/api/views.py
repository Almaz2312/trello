from django.contrib.auth import get_user_model, authenticate
from django.http.response import HttpResponseRedirect
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from accounts.api.serializers import (UserSerializer,
                                      ResetPasswordSerializer,
                                      ResetPasswordCompleteSerializer,
                                      ChangePasswordSerializer)
from main import settings

User = get_user_model()


class RegisterAPIView(APIView):

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.create(request.data)
            return Response('Successfully created!', status=status.HTTP_201_CREATED)


class ActivationAPIView(APIView):
    def get(self, request, activation_code):
        user = User.objects.get(activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Successfully activated', status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
            }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):

    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleLoginView(APIView):
    def get(self, request):
        return HttpResponseRedirect(f'{settings.SOCIAL_AUTH_LOGIN_URL}')


class ResetPasswordAPIView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        data = request.data
        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_code(request.data.get('email'))
            return Response('Check your email for code', status=status.HTTP_201_CREATED)


class ResetPasswordCompleteView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordCompleteSerializer)
    def post(self, request):
        data = request.data
        serializer = ResetPasswordCompleteSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Password is successfully updated', status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        data = request.data
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response('Password is successfully updated', status=status.HTTP_201_CREATED)
