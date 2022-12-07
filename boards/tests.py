from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from boards.api.views import BoardListAPIView
from boards.models import Board

User = get_user_model()


class BoardTestView(APITestCase):

    def setUp(self):
        self.user1 = User(email='a@b.com', password='12345678')
        self.user1.save()

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_list_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        boards = Board(title='UNIT TEST', owner=self.get_user(1))
        boards.save()
        board_url = reverse_lazy('board_api')
        request = self.client.get(board_url)
        self.assertEqual(boards.title, 'UNIT TEST')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_POST_request(self):
        self.client.force_authenticate(user=self.user1)
        board_url = reverse_lazy('board_api')
        data = {'title': "TEST UNITTEST"}
        request = self.client.post(board_url, data=data)
        boards = Board.objects.first()
        self.assertEqual(boards.title, 'TEST UNITTEST')
        self.assertEqual(boards.owner, self.user1)
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_PUT_request(self):
        self.client.force_authenticate(user=self.user1)
        board_url = reverse_lazy('board_api')
        self.client.post(board_url, data={'title': 'UnitTest'})
        board = Board.objects.first()
        request = self.client.patch(reverse_lazy('board_api_detail', kwargs={'pk': board.pk}),
                                    data={'title': 'Changed'}, follow=True)
        changed = Board.objects.first()
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(changed.title, 'Changed')
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_PATCH_request(self):
        self.client.force_authenticate(user=self.user1)
        board_url = reverse_lazy('board_api')
        self.client.post(board_url, data={'title': 'UnitTest'})
        board = Board.objects.first()
        request = self.client.patch(reverse_lazy('board_api_detail', kwargs={'pk': board.pk}), data={'title': 'Changed'}, follow=True)
        changed = Board.objects.first()
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(changed.title, 'Changed')
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_DELETE_request(self):
        self.client.force_authenticate(user=self.user1)
        board_url = reverse_lazy('board_api')
        self.client.post(board_url, data={'title': 'UnitTest'})
        data = {'title': 'Changed Test'}
        board = Board.objects.first()
        request = self.client.delete(reverse_lazy('board_api_detail', kwargs={'pk': board.pk}), follow=True)
        self.assertEqual(Board.objects.count(), 0)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)


class MemberTest(APITestCase):
    def test_list_GET_request(self):