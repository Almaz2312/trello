from django.core.mail import send_mail
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from main import settings

User = get_user_model()


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(label='username', max_length=26)
    email = serializers.EmailField(label='email')
    password = serializers.CharField(label='password', min_length=8, write_only=True)
    password2 = serializers.CharField(label='confirm password', min_length=8, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError('This email already exists!!!')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.pop('password2')
        if password2 != password:
            raise ValidationError('Passwords do not match!!!')
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        code = user.create_activation_code()

        activation_link = f'https://127.0.0.1:8000/' \
                          f'{user.activation_code}'
        send_mail(subject='Activation',
                  message=activation_link,
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[user.email],
                  fail_silently=False)
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label='email')
    password = serializers.CharField(min_length=8, write_only=True, label='Password')

    def validate_login(self, email):
        if not User.objects.filter(email=email).exists():
            raise ValidationError('Email does not exists!!!')
        return email

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise ValidationError('Password is not valid')
        return super().validate(attrs)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_login(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email does not exists')
        return email

    def send_verification_code(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email does not exists')
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        user.save()
        send_mail(
            subject='Activation',
            message=f'Ваш код {user.activation_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )


class ResetPasswordCompleteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.CharField()
    password = serializers.CharField(min_length=4)
    password_confirm = serializers.CharField(min_length=4)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('activation_code')
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords are not identical')
        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('User with this email and activation code not found')
        return super().validate(attrs)

    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.activation_code = ''
        user.set_password(password)
        user.save()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=4)
    new_password = serializers.CharField(min_length=4)
    password_confirm = serializers.CharField(min_length=4)

    def validate_old_password(self, password):
        user = self.context['request'].user
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid password')
        return password

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        password_confirm = attrs.get('password_confirm')
        if new_password != password_confirm:
            raise serializers.ValidationError('Passwords are not identical')
        return super().validate(attrs)

    def set_new_password(self):
        user = self.context['request'].user
        password = self.validated_data.get('new_password')
        user.set_password(password)
        user.save()
