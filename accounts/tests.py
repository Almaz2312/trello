from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterTest(APITestCase):
    def test_POST_register(self):
        data = {'username': 'abcdefg', 'email': 'user@example.com', 'password': "123123321", 'password2': "123123321"}
        request = self.client.post(reverse_lazy('api_register'), data=data)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

class ActivationTest(APITestCase):
    def setUp(self):
        self.user1 = User(email='a@b.com', password='123123123', activation_code='123123-asdsad-123123-asdasd')
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_POST_request(self):
        data = {'activation_code': '123123-asdsad-123123-asdasd'}
        request = self.client.post(reverse_lazy('api_activation'), data=data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)


class LoginTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='a@b.com', password='123123123',
                          activation_code='123123-asdsad-123123-asdasd')
        self.user1.is_active = True
        self.user1.save()
        self.user2 = User.objects.create_user(email='b@c.com', password='123123123', username='bc')
        self.user2.save()

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_POST_request(self):
        data = {'email': 'a@b.com', 'password': '123123123'}
        request = self.client.post(reverse_lazy('api_login'), data=data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)


class ResetPassword(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='a@b.com', password='123123123',
                          activation_code='123123-asdsad-123123-asdasd')
        self.user1.is_active = True
        self.user1.save()
        self.user2 = User.objects.create_user(email='b@c.com', password='123123123', username='bc')
        self.user2.save()

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_POST_request(self):
        request = self.client.post(reverse_lazy('api_reset_password'), data={'email': 'a@b.com'})
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

class RestorePasswordCompleteTest(APITestCase):
    def setUp(self):
        self.user1 = User(email='a@b.com', password='123123123',
                          activation_code='123123-asdsad-123123-asdasd')
        self.user1.is_active = True
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_POST_request(self):
        data = {'email': 'a@b.com', 'activation_code': '123123-asdsad-123123-asdasd',
                'password': '12321232al', 'password_confirm': '12321232al'}
        request = self.client.post(reverse_lazy('api_reset_password'),
                                   data=data)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)


class LogoutTest(APITestCase):
    def setUp(self):
        self.user1 = User(email='a@b.com', password='123123123',
                          activation_code='123123-asdsad-123123-asdasd')
        self.user1.is_active = True
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)
    def test_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        token, _ = Token.objects.get_or_create(user=self.user1)
        request = self.client.get(reverse_lazy('api_logout'))
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

class GoogleOAUTHTest(APITestCase):
    def test_GET_request(self):
        request = self.client.get(reverse_lazy('api_google_auth'))
        self.assertEqual(request.status_code, status.HTTP_302_FOUND)