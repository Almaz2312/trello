import datetime

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
from io import BytesIO
from django.core import files

from boards.api.permissions import IsOwnerOrMember
from boards.models import (
    Board, Members, Column,
    Card, CheckList,
    LastSeen, Mark, Favourite,
    Archive, File, MarkCard
)

from boards.api.serializers import (
    BoardSerializer,
    MembersSerializer,
    ColumnSerializer,
    CardSerializer,
    CommentSerializer,
    ChecklistSerializer,
    LastSeenSerializer,
    MarksSerializer,
    FavouriteSerializer,
    ArchiveSerializer,
    MarkCardSerializer,
    FileSerializer,
)


class BoardListAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsOwnerOrMember, ]

    def get(self, request):
        boards = Board.objects.filter(Q(members__member=request.user) | Q(owner=request.user))
        search = self.request.query_params.get('search')
        if search:
            boards = boards.filter(title__icontains=search)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=BoardSerializer)
    def post(self, request):
        serializer = BoardSerializer(owner=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def save(self):
        image = self.background
        img = Image.open(image)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_io = BytesIO()

        img.save(img_io, 'JPEG', optimize=True, quality=70)
        new_image = files.File(img_io, name=image.name)
        return new_image


class BoardDetailUpdateDeleteAPIView(APIView):
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        board = Board.objects.filter(pk=pk)
        if board:
            serializer = BoardSerializer(board[0])
            last_seen, created = LastSeen.objects.get_or_create(user=request.user, board=board[0])
            if not created:
                last_seen.seen = datetime.datetime.now()
                last_seen.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=BoardSerializer)
    def put(self, request, pk):
        board = Board.objects.get(pk=pk)
        serializer = BoardSerializer(board, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=BoardSerializer)
    def patch(self, request, pk):
        board = Board.objects.get(pk=pk)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        board = Board.objects.get(pk=pk)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MembersListAPIView(APIView):

    def get(self, request):
        members = Members.objects.filter(Q(member=request.user) | Q(board__owner=request.user))
        serializer = MembersSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MembersSerializer)
    def post(self, request):
        board = Board.objects.get(id=request.data['board'])

        if board and board.owner == request.user:
            return Response({'Fail': 'Owner Cannot Be A Member'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(member=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MembersDetailUpdateDeleteAPIView(APIView):
    def get(self, request, pk):
        member = MembersSerializer(Members.objects.get(pk=pk))
        return Response(member.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MembersSerializer)
    def put(self, request, pk):
        serializer = MembersSerializer(Members.objects.get(pk=pk), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=MembersSerializer)
    def patch(self, request, pk):
        serializer = MembersSerializer(Members.objects.get(pk=pk), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        member = Members.objects.get(pk=pk)
        if member:
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_404_NOT_FOUND)


class ColumnListCreateAPIView(APIView):
    def get(self, request, board_id):
        board = Board.objects.get(pk=board_id)
        columns = Column.objects.filter(board=board)
        serializer = ColumnSerializer(columns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ColumnSerializer)
    def post(self, request, board_id):
        board = Board.objects.get(pk=board_id)
        serializer = ColumnSerializer(board=board, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ColumnDetailUpdateDeleteAPIView(APIView):
    def get(self, request, pk):
        column = Column.objects.filter(pk=pk)
        if column:
            serializer = ColumnSerializer(column[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        column = Column.objects.get(pk=pk)
        column.delete()
        return Response(status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=ColumnSerializer)
    def put(self, request, pk):
        column = Column.objects.get(pk=pk)
        serializer = ColumnSerializer(column, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=ColumnSerializer)
    def patch(self, request, pk):
        serializer = ColumnSerializer(Column.objects.get(pk=pk), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class CardListCreateAPIView(APIView):
    def get(self, request):
        cards = Card.objects.filter(
            Q(column__board__owner=request.user) |
            Q(column__board__members__member=request.user)
        )
        mark = self.request.query_params.get('mark')
        if mark:
            cards = cards.filter(
                Q(attached_to_card__mark__name__icontains=mark)
            )
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CardSerializer)
    def post(self, request):
        serializer = CardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CardDetailDeleteUpdate(APIView):
    def get(self, request, pk):
        card = Card.objects.filter(pk=pk)
        if card:
            serializer = CardSerializer(card[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        card = Card.objects.get(pk=pk)
        card.delete()
        return Response(status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=CardSerializer)
    def put(self, request, pk):
        card = Card.objects.get(pk=pk)
        serializer = CardSerializer(card, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=CardSerializer)
    def patch(self, request, pk):
        serializer = CardSerializer(Card.objects.get(pk=pk), data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class FileLisCreateAPIView(APIView):
    def get(self, request):
        serializer = FileSerializer(File.objects.filter(Q(board__owner=request.user) | Q(board__members__member=request.user)), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FileSerializer(data=request.data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDetailDeleteAPIView(APIView):
    def get(self, request, pk):
        serializer = File.objects.get(pk=pk)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, pk):
        File.objects.get(pk=pk).delete()
        return Response(status.HTTP_204_NO_CONTENT)


# Fix Here
class CheckListCreateAPIView(APIView):
    def get(self, request):
        checklist = CheckList.objects.filter(Q(card__column__board__owner=request.user) |
                                             Q(card__column__board__members__member=request.user))
        serializer = ChecklistSerializer(checklist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ChecklistSerializer)
    def post(self, request):
        serializer = ChecklistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckDetailUpdateDeleteAPIView(APIView):
    def get(self, request, pk):
        checklist = CheckList.objects.filter(pk=pk)
        if checklist:
            serializer = ChecklistSerializer(checklist[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        checklist = CheckList.objects.get(pk=pk)
        checklist.delete()
        return Response(status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=ChecklistSerializer)
    def put(self, request, pk):
        checklist = CheckList.objects.get(pk=pk)
        serializer = ChecklistSerializer(checklist, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=ChecklistSerializer)
    def patch(self, request, pk):
        checklist = CheckList.objects.get(pk=pk)
        serializer = ChecklistSerializer(checklist, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class LastSeenListAPIView(APIView):
    def get(self, request):
        last_seen = LastSeen.objects.filter(user=request.user).order_by('-seen')[:6]
        serializer = LastSeenSerializer(last_seen, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavouriteListAPIView(APIView):
    def get(self, request):
        favourite = Favourite.objects.filter(author=request.user)
        serializer = FavouriteSerializer(favourite, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FavouriteSerializer)
    def post(self, request):
        serializer = FavouriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavouriteDetailDeleteView(APIView):
    def get(self, request, pk):
        serializer = FavouriteSerializer(Favourite.objects.get(pk=pk))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        Favourite.objects.get(pk=pk).delete()
        return Response(status.HTTP_204_NO_CONTENT)


class MarkListAPIView(APIView):
    def get(self, request):
        marks = Mark.objects.all()
        serializer = MarksSerializer(marks, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MarksSerializer)
    def post(self, request):
        serializer = MarksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkDetailUpdateDeleteAPIView(APIView):
    def get(self, request, pk):
        mark = Mark.objects.get(pk=pk)
        serializer = MarksSerializer(mark)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MarksSerializer)
    def put(self, request, pk):
        mark = Mark.objects.get(pk=pk)
        serializer = MarksSerializer(mark, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=MarksSerializer)
    def patch(self, request, pk):
        serializer = MembersSerializer(Mark.objects.get(pk=pk), request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, pk):
        Mark.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentCreateAPIView(APIView):
    @swagger_auto_schema(request_body=CommentSerializer)
    def post(self, request, card_id):
        card = Card.objects.get(pk=card_id)
        serializer = CommentSerializer(card=card, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class ArchiveListCreateAPIView(APIView):
    def get(self, request):
        archive = Archive.objects.filter(author=request.user)
        serializer = ArchiveSerializer(archive, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ArchiveSerializer)
    def post(self, request):
        board = Board.objects.get(pk=request.data['board'])
        serializer = ArchiveSerializer(author=request.user, board=board)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class ArchiveDetailUpdateDeleteView(APIView):
    def get(self, request, pk):
        serializer = ArchiveSerializer(Archive.objects.get(pk=pk))
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        Archive.objects.get(pk=pk).delete()
        return Response(status.HTTP_204_NO_CONTENT)


class MarkCardCreateView(APIView):
    def create(self, request):
        serializer = MarkCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkCardDetailDeleteView(APIView):
    def get(self, request, pk):
        serializer = MarkCardSerializer(MarkCard.objects.get(pk=pk))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, pk):
        MarkCard.objects.get(pk=pk).delete()
        return Response(status.HTTP_204_NO_CONTENT)


