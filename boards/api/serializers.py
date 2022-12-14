from rest_framework import serializers
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from django.core import files

from boards.models import (Board, Members, Column, Mark,
                           MarkCard, CheckList, LastSeen,
                           Card, Comment, Favourite, Archive,
                           File
                           )

User = get_user_model()


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=36)
    background = serializers.ImageField(required=False)
    owner = serializers.StringRelatedField()

    def compress_image(self, image):
        img = Image.open(image)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_io = BytesIO()
        img.save(img_io, 'JPEG', optimize=True, quality=70)
        new_image = files.File(img_io, name=image.name)
        return new_image

    def create(self, validated_data):
        if 'background' in validated_data:
            validated_data.update({'background': self.compress_image(validated_data['background'])})
        board = Board(**validated_data)
        board.save()
        return board

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.background = validated_data.get('background')
        instance.owner = validated_data.get('owner')
        instance.save()
        return instance

    def to_representation(self, instance):
        reps = super(BoardSerializer, self).to_representation(instance)
        if instance.column.exists():
            reps['columns'] = ColumnSerializer(instance.column.all(), many=True).data
        if instance.members.exists():
            reps['members'] = MembersSerializer(instance.members.all(), many=True).data
        return reps



class MembersSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    member = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    def create(self, validated_data):
        member = Members(**validated_data)
        member.save()
        return member

    def update(self, instance, validated_data):
        instance.member = validated_data.get('member', instance.member)
        instance.board = validated_data.get('board', instance.member)
        instance.save()
        return instance


class ColumnSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    def create(self, validated_data):
        column = Column(**validated_data)
        column.save()
        return column

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.board = validated_data.get('board', instance.board)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super(ColumnSerializer, self).to_representation(instance)
        if not representation.get('pk'):
            return representation

        if instance.card_column.exists():
            representation['cards'] = CardColumnSerializer(instance.card_column.all(), many=True).data
        return representation


class MarksSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    name = serializers.CharField()
    color = serializers.CharField()

    def create(self, validated_data):
        mark = Mark(**validated_data)
        mark.save(())
        return mark

    def update(self, instance, validated_data):
        instance.board = validated_data.get('board', instance.board)
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.save()
        return instance


class MarkCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    mark = serializers.StringRelatedField()
    card = serializers.StringRelatedField()

    def create(self, validated_data):
        mark_card = MarkCard(**validated_data)
        mark_card.save()
        return mark_card


class ChecklistSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    done = serializers.BooleanField(default=False)
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def create(self, validated_data):
        checklist = CheckList(**validated_data)
        checklist.save()
        return checklist

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.done = validated_data.get('done', instance.done)
        instance.save()
        return instance


class LastSeenSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    seen = serializers.DateTimeField()

    def create(self, validated_data):
        LastSeen(**validated_data).save()
        return LastSeen(**validated_data)


class CardColumnSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    due_date = serializers.DateField()
    mark = serializers.StringRelatedField()
    column = serializers.CharField()


class CardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    due_date = serializers.DateField()
    column = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all())

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not representation.get('pk'):
            return representation

        if instance.comment.exists():
            representation['comments'] = CommentSerializer(instance.comment.all(), many=True).data
        if instance.attached_to_card.exists():
            representation['marks'] = MarkCardSerializer(instance.attached_to_card.all(), many=True).data
        if instance.file.exists():
            representation['files'] = FileSerializer(instance.file.all(), many=True).data
        return representation

    def create(self, validated_data):
        card = Card(**validated_data)
        card.save()
        return card

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.column = validated_data.get('column', instance.column)
        instance.save()
        return instance


class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    card = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    created_on = serializers.DateTimeField()

    def create(self, validated_data):
        comment = Comment(**validated_data)
        comment.save()
        return comment


class FavouriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        favourite = Favourite(**validated_data)
        favourite.save()
        return favourite


class ArchiveSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        archive = Archive(**validated_data)
        archive.save()
        return archive


class FileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.FileField()
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def create(self, validated_data):
        file = File(**validated_data)
        file.save()
        return file
