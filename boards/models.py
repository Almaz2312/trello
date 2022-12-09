from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Board(models.Model):
    file_extension_validator = FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'],
                                                      message='File extension not allowed')
    title = models.CharField(max_length=36)
    background = models.ImageField(upload_to='board_background', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True, blank=True)

    def __str__(self):
        return f'{self.title}, {self.pk}'


class Members(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='members')

    def __str__(self):
        return f'{self.member} - {self.board}'


class LastSeen(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seen = models.DateTimeField(auto_now=True)

    def create(self):
        self.board = self.user

    def __str__(self):
        return f'{self.user} - {self.board} - {self.seen}'


class Column(models.Model):
    name = models.CharField(max_length=30)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='column')

    def __str__(self):
        return f'{self.name}, {self.pk}'


class Mark(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='mark')
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Card(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    due_date = models.DateField(blank=True, null=True)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, blank=True, related_name='card_column')

    def __str__(self):
        return f'{self.name}'


class MarkCard(models.Model):
    mark = models.ForeignKey(Mark, related_name='attached_mark', on_delete=models.CASCADE)
    card = models.ForeignKey(Card, related_name='attached_to_card', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.mark} - {self.card}'


class File(models.Model):
    name = models.FileField(upload_to='board_files')
    card = models.ForeignKey(Card, related_name='file', on_delete=models.CASCADE)


class CheckList(models.Model):
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='check_list')

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(max_length=300)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comment')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.card}, {self.text}'


class Favourite(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author.email} - {self.board.title}'


class Archive(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author.email} - {self.board.title}'
