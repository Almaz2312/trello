from rest_framework import serializers
from django.contrib.auth import get_user_model

from boards.models import (Board, Members, Column, Mark,
                           MarkCard, CheckList, LastSeen,
                           Card, Comment, Favourite, Archive,
                           File
                           )

User = get_user_model()


class BoardSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=36)
    background = serializers.ImageField(required=False)
    owner = serializers.StringRelatedField()

    class Meta:
        extra_kwargs = {'id': {'required': True}}

    def create(self, validated_data):
        return Board(**validated_data).save()

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
    member = serializers.StringRelatedField()
    board = serializers.StringRelatedField()

    def create(self, validated_data):
        obj = Board.objects.get(id=validated_data['board'])
        member = Members(
            member=validated_data['member'],
            board=obj
        )

        return member.save()

    def update(self, instance, validated_data):
        instance.member = validated_data.get('member', instance.member)
        instance.board = validated_data.get('board', instance.member)
        instance.save()
        return instance


class ColumnSerializer(serializers.Serializer):
    name = serializers.CharField()
    board = serializers.StringRelatedField()

    def create(self, validated_data):
        return Column(**validated_data).save()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.board = validated_data.get('board', instance.board)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super(ColumnSerializer, self).to_representation(instance)
        if instance.card_column.exists():
            representation['cards'] = CardColumnSerializer(instance.card_column.all(), many=True).data
        return representation


class MarksSerializer(serializers.Serializer):
    board = serializers.StringRelatedField()
    name = serializers.CharField()
    color = serializers.CharField()

    def create(self, validated_data):
        return Mark(**validated_data).save(())

    def update(self, instance, validated_data):
        instance.board = validated_data.get('board', instance.board)
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.save()
        return instance


class MarkCardSerializer(serializers.Serializer):
    mark = serializers.StringRelatedField()
    card = serializers.StringRelatedField()

    def create(self, validated_data):
        return MarkCard(**validated_data).save()


class ChecklistSerializer(serializers.Serializer):
    name = serializers.CharField()
    done = serializers.BooleanField(default=False)
    card = serializers.StringRelatedField()

    def create(self, validated_data):
        return CheckList(**validated_data).save()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.done = validated_data.get('done', instance.done)
        instance.save()
        return instance


class LastSeenSerializer(serializers.Serializer):
    board = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    seen = serializers.DateTimeField()

    def create(self, validated_data):
        return LastSeen(**validated_data).save()


class CardColumnSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    due_date = serializers.DateField()
    mark = serializers.StringRelatedField()
    column = serializers.CharField()


class CardSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    due_date = serializers.DateField()
    mark = serializers.StringRelatedField()
    column = serializers.CharField()

    def create(self, validated_data):
        return Card(**validated_data).save()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.mark = validated_data.get('mark', instance.mark)
        instance.column = validated_data.get('column', instance.column)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.comment.exists():
            representation['comments'] = CommentSerializer(instance.comment.all(), many=True).data
        if instance.attached_to_card.exists():
            representation['marks'] = MarkCardSerializer(instance.attached_to_card.all(), many=True).data
        if instance.file.exists():
            representation['files'] = FileSerializer(instance.file.all(), many=True).data
        return representation


class CommentSerializer(serializers.Serializer):
    text = serializers.CharField()
    card = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    created_on = serializers.DateTimeField()

    def create(self, validated_data):
        return Comment(**validated_data).save()


class FavouriteSerializer(serializers.Serializer):
    board = serializers.StringRelatedField()
    author = serializers.StringRelatedField()

    def create(self, validated_data):
        return Favourite(**validated_data).save()


class ArchiveSerializer(serializers.Serializer):
    board = serializers.StringRelatedField()
    author = serializers.StringRelatedField()

    def create(self, validated_data):
        return Archive(**validated_data).save()


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
    card = serializers.StringRelatedField()

    def create(self, validated_data):
        return File(**validated_data).save()
