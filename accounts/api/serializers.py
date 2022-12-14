from django.core.mail import send_mail
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from main import settings

User = get_user_model()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(label='username', max_length=26)
    email = serializers.EmailField(label='email')
    password = serializers.CharField(label='password', min_length=8, write_only=True)
    password2 = serializers.CharField(label='confirm password', min_length=8, write_only=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email already exists!!!')
        return email

    def validate(self, attrs):
        attrs._mutable = True
        password = attrs.get('password')
        password2 = attrs.pop('password2')
        if password2 != password:
            raise ValidationError('Passwords do not match!!!')
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**self.validated_data)
        user.is_active = False
        code = user.create_activation_code()

        # activation_link = f'{user.activation_code}'
        # send_mail(subject='Activation',
        #           message=activation_link,
        #           from_email=settings.EMAIL_HOST_USER,
        #           recipient_list=[user.email],
        #           fail_silently=False)
        user.save()
        return user


class AccountActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField()

    def validate(self, attrs):
        activation_code = attrs.get('activation_code')
        user = User.objects.get(activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return super().validate(attrs)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label='email')
    password = serializers.CharField(min_length=8, write_only=True, label='Password')


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
