import datetime

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

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

from boards.api.permissions import IsBoardOwner, IsBoardOwnerOrMember


class BoardListAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsBoardOwner]


    @swagger_auto_schema(responses={200: BoardSerializer(many=True)})
    def get(self, request):
        boards = Board.objects.filter(Q(members__member=request.user) | Q(owner=request.user))
        search = self.request.query_params.get('search')
        if search:
            boards = boards.filter(title__icontains=search)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=BoardSerializer)
    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class BoardDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsBoardOwner, ]

    def get_object(self, pk):
        board = Board.objects.get(pk=pk)
        return board

    def get(self, request, pk):
        board = self.get_object(pk)
        self.check_object_permissions(request, board)
        serializer = BoardSerializer(board)
        last_seen, created = LastSeen.objects.get_or_create(user=request.user, board=board)
        if not created:
            last_seen.seen = datetime.datetime.now()
            last_seen.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=BoardSerializer)
    def put(self, request, pk):
        board = self.get_object(pk)
        self.check_object_permissions(request, board)
        serializer = BoardSerializer(board, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=BoardSerializer)
    def patch(self, request, pk):
        board = self.get_object(pk)
        self.check_object_permissions(request, board)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        board = self.get_object(pk)
        self.check_object_permissions(request, board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MembersListAPIView(APIView):
    permission_classes = [IsBoardOwner]

    def get(self, request):
        members = Members.objects.filter(Q(member=request.user) | Q(board__owner=request.user))
        for member in members:
            self.check_object_permissions(request, member.board)
        serializer = MembersSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MembersSerializer)
    def post(self, request):
        board = Board.objects.get(id=request.data['board'])
        self.check_object_permissions(request, board)

        # Owner can not be a member
        if request.data['member'] == board.owner.pk:
            return Response({'Fail': 'Owner Cannot Be A Member'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class MembersDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsBoardOwner]

    def get_object(self, pk):
        member = Members.objects.get(pk=pk)
        return member

    def get(self, request, pk):
        board = self.get_object(pk).board
        self.check_object_permissions(request, board)
        member = MembersSerializer(self.get_object(pk))
        return Response(member.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MembersSerializer)
    def put(self, request, pk):
        member = self.get_object(pk)
        self.check_object_permissions(request, member.board)
        serializer = MembersSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=MembersSerializer)
    def patch(self, request, pk):
        board = self.get_object(pk).board
        self.check_object_permissions(request, board)
        serializer = MembersSerializer(self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = self.get_object(pk)
        self.check_object_permissions(request, member.board)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ColumnListCreateAPIView(APIView):
    permission_classes = [IsBoardOwner]

    def get(self, request):
        columns = Column.objects.filter(Q(board__owner=request.user) | Q(board__members__member=request.user))
        for column in columns:
            self.check_object_permissions(request, column.board)
        serializer = ColumnSerializer(columns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ColumnSerializer)
    def post(self, request):
        board = Board.objects.get(pk=request.data['board'])
        self.check_object_permissions(request, board)
        serializer = ColumnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ColumnDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsBoardOwner]

    def get_object(self, pk):
        column = Column.objects.get(pk=pk)
        return column

    def get(self, request, pk):
        column = self.get_object(pk)
        self.check_object_permissions(request, column[0].board)
        serializer = ColumnSerializer(column[0])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        column = Column.objects.get(pk=pk)
        self.check_object_permissions(request, column.board)
        column.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=ColumnSerializer)
    def put(self, request, pk):
        column = self.get_object(pk)
        self.check_object_permissions(request, column.board)
        serializer = ColumnSerializer(column, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ColumnSerializer)
    def patch(self, request, pk):
        self.check_object_permissions(request, self.get_object(pk).board)
        serializer = ColumnSerializer(self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CardListCreateAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get(self, request):
        cards = Card.objects.filter(
            Q(column__board__owner=request.user) |
            Q(column__board__members__member=request.user)
        )
        for card in cards:
            self.check_object_permissions(request, card.column.board)
        mark = self.request.query_params.get('mark')
        if mark:
            cards = cards.filter(
                Q(attached_to_card__mark__name__icontains=mark)
            )
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CardSerializer)
    def post(self, request):
        board = Column.objects.get(pk=request.data['column']).board
        self.check_object_permissions(request, board)
        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class CardDetailDeleteUpdate(APIView):

    def get_object(self, pk):
        card = Card.objects.get(pk=pk)
        return card

    def get(self, request, pk):
        card = self.get_object(pk)
        self.check_object_permissions(request, card[0].column.board)
        serializer = CardSerializer(card[0])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        card = self.get_object(pk)
        self.check_object_permissions(request, card.column.board)
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=CardSerializer)
    def put(self, request, pk):
        card = self.get_object(pk)
        self.check_object_permissions(request, card.column.board)
        serializer = CardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=CardSerializer)
    def patch(self, request, pk):
        self.check_object_permissions(request, self.get_object(pk).column.board)
        serializer = CardSerializer(self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class FileListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsBoardOwnerOrMember]

    def get(self, request):
        obj = File.objects.filter(Q(card__column__board__owner=request.user) | Q(card__column__board__members__member=request.user))
        for fi in obj:
            self.check_object_permissions(request, fi.card.column.board)
        serializer = FileSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FileSerializer)
    def post(self, request):
        board = Card.objects.get(pk=request.data['card']).column.board
        self.check_object_permissions(request, board)
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FileDetailDeleteAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get_object(self, pk):
        file = File.objects.get(pk=pk)
        return file

    def get(self, request, pk):
        board = self.get_object(pk).card.column.board
        self.check_object_permissions(request, board)
        file = self.get_object(pk)
        serializer = FileSerializer(data=file)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        self.check_object_permissions(request, self.get_object(pk).card.column.board)
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckListCreateAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get(self, request):
        checklist = CheckList.objects.filter(Q(card__column__board__owner=request.user) |
                                             Q(card__column__board__members__member=request.user))
        for check in checklist:
            self.check_object_permissions(request, check.card.column.board)

        serializer = ChecklistSerializer(checklist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ChecklistSerializer)
    def post(self, request):
        board = Card.objects.get(pk=request.data['card']).column.board
        self.check_object_permissions(request, board)
        serializer = ChecklistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CheckDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get_object(self, pk):
        checklist = CheckList.objects.get(pk=pk)
        return checklist

    def get(self, request, pk):
        checklist = self.get_object(pk)
        self.check_object_permissions(request, checklist.card.column.board)
        serializer = ChecklistSerializer(checklist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        checklist = self.get_object(pk)
        self.check_object_permissions(request, checklist.card.column.board)
        checklist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=ChecklistSerializer)
    def put(self, request, pk):
        checklist = self.get_object(pk)
        self.check_object_permissions(request, checklist.card.column.board)
        serializer = ChecklistSerializer(checklist, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ChecklistSerializer)
    def patch(self, request, pk):
        checklist = self.get_object(pk)
        self.check_object_permissions(request, checklist.card.column.board)
        serializer = ChecklistSerializer(checklist, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LastSeenListAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get(self, request):
        last_seen = LastSeen.objects.filter(user=request.user).order_by('-seen')[:6]
        self.check_object_permissions(request, last_seen.board)
        serializer = LastSeenSerializer(last_seen, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavouriteListAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get(self, request):
        favourite = Favourite.objects.filter(author=request.user)
        for fav in favourite:
            self.check_object_permissions(request, fav.board)
        serializer = FavouriteSerializer(favourite, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FavouriteSerializer)
    def post(self, request):
        self.check_object_permissions(request, Board.objects.get(pk=request.data['board']))
        serializer = FavouriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FavouriteDetailDeleteView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get_object(self, pk):
        favourite = Favourite.objects.get(pk=pk)
        return favourite

    def get(self, request, pk):
        self.check_object_permissions(request, self.get_object(pk).board)
        serializer = FavouriteSerializer(self.get_object(pk))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        favourite = self.get_object(pk)
        self.check_object_permissions(request, favourite.board)
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkListAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

# ValueError: Cannot query "a@b.com": Must be "Board" instance. On Get test
    @swagger_auto_schema(responses={200: MarksSerializer(many=True)})
    def get(self, request):

        marks = Mark.objects.filter(board__owner=request.user)
        serializer = MarksSerializer(marks, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MarksSerializer)
    def post(self, request):
        self.check_object_permissions(request, Board.objects.get(pk=request.data['board']))
        serializer = MarksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class MarkDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get_object(self, pk):
        mark = Mark.objects.get(pk=pk)
        return mark

    def get(self, request, pk):
        mark = self.get_object(pk)
        self.check_object_permissions(request, mark.board)
        serializer = MarksSerializer(mark)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MarksSerializer)
    def put(self, request, pk):
        mark = self.get_object(pk)
        self.check_object_permissions(request, mark.board)
        serializer = MarksSerializer(mark, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=MarksSerializer)
    def patch(self, request, pk):
        mark = self.get_object(pk)
        self.check_object_permissions(request, mark.board)
        serializer = MarksSerializer(mark, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.check_object_permissions(request, self.get_object(pk).board)
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentCreateAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    @swagger_auto_schema(request_body=CommentSerializer)
    def post(self, request, card_id):
        card = Card.objects.get(pk=card_id)
        self.check_object_permissions(request, card.column.board)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(card=card, author=request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ArchiveListCreateAPIView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get(self, request):
        archive = Archive.objects.filter(author=request.user)
        for arch in archive:
            self.check_object_permissions(request, arch.board)
        serializer = ArchiveSerializer(archive, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ArchiveSerializer)
    def post(self, request):
        board = Board.objects.get(pk=request.data['board'])
        self.check_object_permissions(request, board)
        serializer = ArchiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ArchiveDetailUpdateDeleteView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get_object(self, pk):
        archive = Archive.objects.get(pk=pk)
        return archive

    def get(self, request, pk):
        serializer = ArchiveSerializer(self.get_object(pk))
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkCardCreateView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def create(self, request):
        self.check_object_permissions(request, Card.objects.get('card').column.board)
        serializer = MarkCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class MarkCardDetailDeleteView(APIView):
    permission_classes = [IsBoardOwnerOrMember]

    def get_object(self, pk):
        mark_card = MarkCard.objects.get(pk=pk)
        return mark_card

    def get(self, request, pk):
        self.check_object_permissions(request, Card.objects.get('card').column.board)
        serializer = MarkCardSerializer(self.get_object(pk))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        self.check_object_permissions(request, self.get_object(pk).card.column.board)
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


