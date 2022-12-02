from django.http import HttpRequest
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from boards.api.views import BoardListAPIView
from boards.models import Board

User = get_user_model()


class BoardListCreateTestView(APITestCase):

    def setUp(self):
        self.user1 = User(email='a@b.com', password='12345678')
        self.user1.save()

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_get_object(self):
        self.client.force_login(self.get_user(1))
        boards = Board(title='UNIT TEST', owner=self.get_user(1))
        boards.save()
        board_url = reverse_lazy('board_api')
        request = self.client.get(board_url)
        self.assertEqual(boards.title, 'UNIT TEST')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    # def test_can_save_a_POST_request(self):
    #     data = {'title': "TEST UNITTEST"}
    #     self.client.force_login(self.get_user(1))
    #     self.client.post('board_api', data=data)
    #     self.assertEqual(Board.objects.count(), 1)
    #     # BoardListAPIView.post(self, request)
    #     boards = Board.objects.first()
    #     self.assertEqual(boards.title, 'TEST UNITTEST')
    #     self.assertEqual(boards.owner, self.user1)
