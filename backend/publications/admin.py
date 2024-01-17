from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Comment, Post


class TreePostContentsAdmin(TreeAdmin):
    form = movenodeform_factory(Comment)


admin.site.register(Comment, TreePostContentsAdmin)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'author',)
    search_fields = ('text',)
    list_filter = ('created_at', 'author',)
    empty_value_display = '-пусто-'

    fieldsets = (
        ('Главное', {'fields': ('title', 'author')}),
        ('Текст', {'fields': ('text',)}),
    )
    empty_value_display = '-пусто-'
