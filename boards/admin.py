from django.contrib import admin
from boards.models import Card, Column, Board, Favourite, Mark, CheckList

admin.site.register(Card)
admin.site.register(Column)
admin.site.register(Board)
admin.site.register(Favourite)
admin.site.register(Mark)
admin.site.register(CheckList)
