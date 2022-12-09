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
        Board(**validated_data).save()
        return Board(**validated_data)

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
    name = serializers.CharField()
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    def create(self, validated_data):
        Column(**validated_data).save()
        return Column(**validated_data)

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
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    name = serializers.CharField()
    color = serializers.CharField()

    def create(self, validated_data):
        Mark(**validated_data).save(())
        return Mark(**validated_data)

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
        MarkCard(**validated_data).save()
        return MarkCard(**validated_data)


class ChecklistSerializer(serializers.Serializer):
    name = serializers.CharField()
    done = serializers.BooleanField(default=False)
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def create(self, validated_data):
        CheckList(**validated_data).save()
        return CheckList(**validated_data)

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
        LastSeen(**validated_data).save()
        return LastSeen(**validated_data)


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
        Card(**validated_data).save()
        return Card(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.column = validated_data.get('column', instance.column)
        instance.save()
        return instance


class CommentSerializer(serializers.Serializer):
    text = serializers.CharField()
    card = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    created_on = serializers.DateTimeField()

    def create(self, validated_data):
        Comment(**validated_data).save()
        return Comment(**validated_data)


class FavouriteSerializer(serializers.Serializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        Favourite(**validated_data).save()
        return Favourite(**validated_data)


class ArchiveSerializer(serializers.Serializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        Archive(**validated_data).save()
        return Archive(**validated_data)


class FileSerializer(serializers.Serializer):
    name = serializers.FileField()
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def create(self, validated_data):
        File(**validated_data).save()
        return File(**validated_data)
