from django.contrib.auth import get_user_model, authenticate
from django.http.response import HttpResponseRedirect
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from accounts.api.serializers import (UserSerializer,
                                      ResetPasswordSerializer,
                                      ResetPasswordCompleteSerializer,
                                      ChangePasswordSerializer, LoginSerializer,
                                      AccountActivationSerializer)
from main import settings

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.create(request.data)
            return Response('Successfully created!', status=status.HTTP_201_CREATED)


class ActivationAPIView(APIView):
    permission_classes = [AllowAny, ]
    @swagger_auto_schema(request_body=AccountActivationSerializer)
    def post(self, request):
        serializer = AccountActivationSerializer(data=request.data)
        if serializer.is_valid():
            return Response('Successfully activated', status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'Token': f'Token {token.key}',
            }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):

    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleLoginView(APIView):

    def get(self, request):
        # return HttpResponseRedirect(f'{settings.SOCIAL_AUTH_LOGIN_URL}')
        return HttpResponseRedirect(f'{settings.SOCIAL_AUTH_LOGIN_URL}')

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        data = request.data
        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid():
            serializer.send_verification_code(request.data.get('email'))
            return Response('Check your email for code', status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordCompleteView(APIView):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(request_body=ResetPasswordCompleteSerializer)
    def post(self, request):
        data = request.data
        serializer = ResetPasswordCompleteSerializer(data=data)
        if serializer.is_valid():
            serializer.set_new_password()
            return Response('Password is successfully updated', status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        data = request.data
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response('Password is successfully updated', status=status.HTTP_201_CREATED)
