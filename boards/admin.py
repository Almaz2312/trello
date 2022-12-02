from django.contrib import admin
from boards.models import (Card, Column, Board, Comment,
                           Favourite, Mark, CheckList,
                           LastSeen, Members, MarkCard, File
                           )


admin.site.register(Card)
admin.site.register(Column)
admin.site.register(Board)
admin.site.register(Favourite)
admin.site.register(Mark)
admin.site.register(CheckList)
admin.site.register(LastSeen)
admin.site.register(Members)
admin.site.register(MarkCard)
admin.site.register(File)
admin.site.register(Comment)
