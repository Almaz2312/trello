from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from boards.api.views import BoardListAPIView
from boards.models import Board, Members, Column, Card, CheckList, Archive, File, Comment, Mark, Favourite

User = get_user_model()

def create_board_instance(self):
    board = Board(title='some title', owner=self.user1)
    board.save()
    return board

def create_member_instance(self, board):
    member = Members(member=self.user1, board=board)
    member.save()
    return member


class BoardTestView(APITestCase):

    def setUp(self):
        self.board_url = reverse_lazy('board_api')
        self.user1 = User(email='a@b.com', password='12345678')
        self.user1.save()

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_list_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        boards = Board(title='UNIT TEST', owner=self.user1)
        boards.save()
        request = self.client.get(self.board_url)
        self.assertEqual(boards.title, 'UNIT TEST')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_POST_request(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': "TEST UNITTEST"}
        request = self.client.post(self.board_url, data=data)
        boards = Board.objects.first()
        self.assertEqual(boards.title, 'TEST UNITTEST')
        self.assertEqual(boards.owner, self.user1)
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_PUT_request(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.board_url, data={'title': 'UnitTest'})
        board = Board.objects.first()
        request = self.client.put(reverse_lazy('board_api_detail', kwargs={'pk': board.pk}),
                                    data={'title': 'Changed'}, follow=True)
        changed = Board.objects.first()
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(changed.title, 'Changed')
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_PATCH_request(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.board_url, data={'title': 'UnitTest'})
        board = Board.objects.first()
        request = self.client.patch(reverse_lazy('board_api_detail', kwargs={'pk': board.pk}), data={'title': 'Changed'}, follow=True)
        changed = Board.objects.first()
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(changed.title, 'Changed')
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_DELETE_request(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.board_url, data={'title': 'UnitTest'})
        data = {'title': 'Changed Test'}
        board = Board.objects.first()
        request = self.client.delete(reverse_lazy('board_api_detail', kwargs={'pk': board.pk}), follow=True)
        self.assertEqual(Board.objects.count(), 0)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)


class MemberTest(APITestCase):
    def setUp(self):

        self.user1 = User(email='a@b.com', password='123123123')
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()
        self.member_url = reverse_lazy('member_api')

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        request = self.client.get(self.member_url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_POST_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        request = self.client.post(self.member_url, data={'board': board.pk, 'member': self.user2.pk})
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_PATCH_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        second = Board(title='Second Board')
        second.save()
        member = create_member_instance(self, board=board)
        request = self.client.patch(
            reverse_lazy('member_api_detail', kwargs={'pk': member.pk}),
            {'board': second.pk})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_PUT_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        second = Board(title='Second Board')
        second.save()
        member = create_member_instance(self, board=board)
        request = self.client.put(
            reverse_lazy('member_api_detail', kwargs={'pk': member.pk}),
            {'board': second.pk, 'member': self.user1.pk})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_DELETE_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        member = create_member_instance(self, board=board)
        request = self.client.delete(reverse_lazy('member_api_detail', kwargs={'pk': 1}))
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)


def create_column_instance(self, board):
    column = Column(name='New Column Name', board=board)
    column.save()
    return column


class ColumnTest(APITestCase):
    def setUp(self):

        self.user1 = User(email='a@b.com', password='123123123')
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()
        self.column_url = reverse_lazy('column_api')

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        request = self.client.get(self.column_url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_POST_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        request = self.client.post(self.column_url, {'name': 'Testing Name',
                                                     'board': board.pk})
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_PATCH_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        request = self.client.patch(reverse_lazy('column_api_detail', kwargs={'pk': column.pk}),
                                    data={'name': 'PATCHED NAME'})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_PUT_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        second = Board(title='Second Board', owner=self.user1)
        second.save()
        column = create_column_instance(self, board)
        request = self.client.put(reverse_lazy('column_api_detail', kwargs={'pk': column.pk}),
                                    data={'name': 'PUT NAME', 'board': board.pk})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_DELETE_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        request = self.client.delete(reverse_lazy('column_api_detail', kwargs={'pk': column.pk}))
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

def create_card_instance(self, column):
    card = Card(name='Some Card Name', description='Some first descr',
                due_date='2022-12-31', column=column)
    card.save()
    return card


class CardTest(APITestCase):
    def setUp(self):

        self.user1 = User(email='a@b.com', password='123123123')
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()
        self.card_url = reverse_lazy('card_api')

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        request = self.client.get(self.card_url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_POST_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        request = self.client.post(self.card_url, {'name': 'POST Card Name', 'description': 'POST descr',
                'due_date': '2022-12-31', 'column': column.pk})
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_PATCH_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        request = self.client.patch(reverse_lazy('card_api_detail', kwargs={'pk': card.pk}),
                                    data={'name': 'PATCHED NAME'})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_PUT_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        request = self.client.put(reverse_lazy('card_api_detail', kwargs={'pk': card.pk}),
                                    data={'name': 'PUT Card Name', 'description': 'PUT descr',
                'due_date': '2022-12-30', 'column': column.pk})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_DELETE_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        request = self.client.delete(reverse_lazy('card_api_detail', kwargs={'pk': card.pk}))
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)


def create_checklist_instance(self, card):
    check = CheckList(name='Some checklist name', done=True, card=card)
    check.save()
    return check


class CheckListTest(APITestCase):
    def setUp(self):

        self.user1 = User(email='a@b.com', password='123123123')
        self.user1.save()
        self.user2 = User(email='b@c.com', password='123123123', username='bc')
        self.user2.save()
        self.checklist_url = reverse_lazy('checklist_api')

        return self.user1, self.user2

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_GET_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        checklist = create_checklist_instance(self, card)
        request = self.client.get(self.checklist_url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_POST_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        request = self.client.post(self.checklist_url, {'name': 'POST CheckList Name', 'done': True,
                'card': card.pk})
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_PATCH_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        checklist = create_checklist_instance(self, card)
        request = self.client.patch(reverse_lazy('checklist_api_detail', kwargs={'pk': checklist.pk}), {'name': 'PATCH CheckList Name'})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_PUT_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        checklist = create_checklist_instance(self, card)
        request = self.client.put(reverse_lazy('checklist_api_detail', kwargs={'pk': checklist.pk}), {'name': 'PUT CheckList Name', 'done': True,
                                                        'card': card.pk})
        self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

    def test_DELETE_request(self):
        self.client.force_authenticate(user=self.user1)
        board = create_board_instance(self)
        column = create_column_instance(self, board)
        card = create_card_instance(self, column)
        checklist = create_checklist_instance(self, card)
        request = self.client.delete(reverse_lazy('checklist_api_detail', kwargs={'pk': checklist.pk}))
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

def create_archive_instance(self, board, user):
    archive = Archive(board=board, author=user)
    archive.save()
    return archive


class ArchiveTest(APITestCase):

        def setUp(self):
            self.user1 = User(email='a@b.com', password='123123123')
            self.user1.save()
            self.user2 = User(email='b@c.com', password='123123123', username='bc')
            self.user2.save()
            self.archive_url = reverse_lazy('archive_api')

            return self.user1, self.user2

        def get_user(self, pk):
            return User.objects.get(pk=pk)

        def test_GET_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            archive = create_archive_instance(self, board, self.user1)
            request = self.client.get(self.archive_url)
            self.assertEqual(request.status_code, status.HTTP_200_OK)

        def test_POST_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            request = self.client.post(self.archive_url, data={'board': board.pk, 'author': self.user1.pk})
            self.assertEqual(request.status_code, status.HTTP_201_CREATED)


        def test_DELETE_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            archive = create_archive_instance(self, board, user=self.user1)
            request = self.client.delete(reverse_lazy('archive_api_detail', kwargs={'pk': archive.pk}))
            self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

# def create_file_instance(self, card):
#     file = SimpleUploadedFile(name='Some_text', content=b'texting text to text', content_type='video/mp4')
#     f = File(card=card, name=file)
#     f.save()
#     return f
#
# class FileAPITest(APITestCase):
#     def setUp(self):
#         self.user1 = User(email='a@b.com', password='123123123')
#         self.user1.save()
#         self.user2 = User(email='b@c.com', password='123123123', username='bc')
#         self.user2.save()
#         self.file_url = reverse_lazy('file_api')
#
#         return self.user1, self.user2
#
#     def get_user(self, pk):
#         return User.objects.get(pk=pk)
#
#     def test_GET_request(self):
#         self.client.force_authenticate(user=self.user1)
#         board = create_board_instance(self)
#         column = create_column_instance(self, board)
#         card = create_card_instance(self, column)
#         f = create_file_instance(self, card)
#         request = self.client.get(self.file_url)
#         self.assertEqual(request.status_code, status.HTTP_200_OK)
#
#     def test_POST_request(self):
#         self.client.force_authenticate(user=self.user1)
#         board = create_board_instance(self)
#         column = create_column_instance(self, board)
#         card = create_card_instance(self, column)
#         file = SimpleUploadedFile(name='Some_text', content=b'texting text to text', content_type='video/mp4')
#         request = self.client.post(self.file_url, data={'name': file, 'card': card.pk})
#         self.assertEqual(request.status_code, status.HTTP_201_CREATED)
#
#     def test_DELETE_request(self):
#         self.client.force_authenticate(user=self.user1)
#         board = create_board_instance(self)
#         column = create_column_instance(self, board)
#         card = create_card_instance(self, column)
#         cr = create_file_instance(self, card)
#         request = self.client.delete(reverse_lazy('file_api_detail', kwargs={'pk': cr.pk}))
#         self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)


def create_comment_instance(self, card,):
    comment = Comment(text='Some text', card=card, author=self.user1, created_on='2022-12-09T00:45:05.845Z')
    comment.save()
    return comment


class CommentTest(APITestCase):

        def setUp(self):
            self.user1 = User(email='a@b.com', password='123123123')
            self.user1.save()
            self.user2 = User(email='b@c.com', password='123123123', username='bc')
            self.user2.save()

            return self.user1, self.user2

        def get_user(self, pk):
            return User.objects.get(pk=pk)

        def test_POST_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            column = create_column_instance(self, board)
            card = create_card_instance(self, column)
            request = self.client.post(reverse_lazy('comment_api', kwargs={'card_id': card.pk}),
                                       data={'text': 'Some Text',
                                             'created_on': '2022-12-09T00:45:05.845Z'})
            self.assertEqual(request.status_code, status.HTTP_201_CREATED)



def create_mark_instance(self, board):
    mark = Mark(board=board, name='Some Name', color='Blue')
    mark.save()
    return mark


class MarkTest(APITestCase):

        def setUp(self):
            self.user1 = User(email='a@b.com', password='123123123')
            self.user1.save()
            self.user2 = User(email='b@c.com', password='123123123', username='bc')
            self.user2.save()
            self.mark_url = reverse_lazy('mark_api')

            return self.user1, self.user2

        def get_user(self, pk):
            return User.objects.get(pk=pk)

        # Problem with GET
        def test_GET_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            mark = create_mark_instance(self, board)
            request = self.client.get(self.mark_url)
            self.assertEqual(request.status_code, status.HTTP_200_OK)

        def test_POST_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            request = self.client.post(self.mark_url, data={'board': board.pk, 'name': 'Some Name', 'color': 'Blue'})
            self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        def test_PATCH_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            mark = create_mark_instance(self, board)
            request = self.client.patch(reverse_lazy('mark_api_detail', kwargs={'pk': mark.pk}),
                                        {'name': 'PATCH Mark Name', 'color': 'random'})
            self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)

        def test_PUT_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            mark = create_mark_instance(self, board)
            request = self.client.put(reverse_lazy('mark_api_detail', kwargs={'pk': mark.pk}),
                                        {'board': board.pk, 'name': 'PUT Mark Name', 'color': 'PUT Green'})
            self.assertEqual(request.status_code, status.HTTP_202_ACCEPTED)


        def test_DELETE_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            mark = create_mark_instance(self, board)
            request = self.client.delete(reverse_lazy('mark_api_detail', kwargs={'pk': mark.pk}))
            self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)



def create_favourite_instance(self, board, user):
    favourite = Favourite(board=board, author=user)
    favourite.save()
    return favourite


class FavouriteTest(APITestCase):

        def setUp(self):
            self.user1 = User(email='a@b.com', password='123123123')
            self.user1.save()
            self.user2 = User(email='b@c.com', password='123123123', username='bc')
            self.user2.save()
            self.favourite_url = reverse_lazy('favourite_api')

            return self.user1, self.user2

        def get_user(self, pk):
            return User.objects.get(pk=pk)

        def test_GET_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            favourite = create_favourite_instance(self, board, self.user1)
            request = self.client.get(self.favourite_url)
            self.assertEqual(request.status_code, status.HTTP_200_OK)

        def test_POST_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            request = self.client.post(self.favourite_url, data={'board': board.pk, 'author': self.user1.pk})
            self.assertEqual(request.status_code, status.HTTP_201_CREATED)


        def test_DELETE_request(self):
            self.client.force_authenticate(user=self.user1)
            board = create_board_instance(self)
            favourite = create_favourite_instance(self, board, user=self.user1)
            request = self.client.delete(reverse_lazy('favourite_api_detail', kwargs={'pk': favourite.pk}))
            self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)
