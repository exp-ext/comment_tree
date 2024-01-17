from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

from .serializers import create_comment_node_serializer, create_post_comment_serializer

User = get_user_model()


class AbstractPost(models.Model):
    """
    Абстрактный класс модели для постов, предоставляющий базовую структуру для постов в блоге или на форуме.

    ## Methods:
    - get_post_with_comments: Возвращает сериализованные данные поста, включая всё дерево комментариев.
    - get_comments_tree: Создает и возвращает сериализованные данные дерева комментариев, начиная с комментариев первого уровня.

    ## Attributes:
    - created_at (`DateTimeField`): Дата и время создания поста.
    - updated_at (`DateTimeField`): Дата и время последнего обновления поста.
    - title (`CharField`): Заголовок поста.
    - text (`TextField`): Текст поста.
    - author (`ForeignKey`): Ссылка на пользователя, являющегося автором поста.

    ## Meta:
    - ordering: Порядок сортировки объектов модели (по умолчанию - в обратном порядке даты создания).
    - abstract: Указывает, что класс является абстрактным и не предназначен для создания таблиц в базе данных.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(_('заголовок поста'), max_length=80, unique=True)
    text = models.TextField(_('текст поста'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('автор'))

    class Meta:
        ordering = ('-created_at',)
        abstract = True

    def get_post_with_comments(self):
        serializer_class = create_post_comment_serializer(self.__class__)
        return serializer_class(self).data

    def get_comments_tree(self):
        comments = self.comments.filter(depth=1)
        serializer_class = create_comment_node_serializer(self.comments.model)
        return serializer_class(comments, many=True).data


class AbstractComment(MP_Node):
    """
    Абстрактный класс модели комментария, предоставляющий базовую структуру для комментариев.
    Этот класс используется как базовый для создания конкретных моделей комментариев.

    ## Methods:
    - save: Изменяет атрибут inverted_rating для используемого для сортировки.
    - get_comments_deeper_from_node: Возвращает сериализованные данные комментариев,
    начиная с текущего узла дерева комментариев c порядком сортировки по рейтингу от высокого к низкому.
    - add_point: Увеличивает рейтинг комментария на один.
    - cut_point: Уменьшает рейтинг комментария на один.
    - point_operation: Статический метод для обработки операций изменения рейтинга. Принимает экземпляр комментария и операнд ('+' или '-').

    ## Attributes:
    - created_at (`DateTimeField`): Дата и время создания комментария.
    - user (`ForeignKey`): Ссылка на пользователя, являющегося автором комментария.
    - post (`ForeignKey`): Ссылка на пост, к которому относится комментарий.
    - text (`TextField`): Текст комментария.
    - rating (`IntegerField`): Рейтинг комментария.
    - inverted_rating (`IntegerField`): Инвертированный рейтинг комментария для сортировки.
    - node_order_by (`tuple`): Порядок сортировки узлов в дереве комментариев.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('автор комментария'))
    post = models.ForeignKey(AbstractPost, on_delete=models.CASCADE, related_name='comments', verbose_name=_('комментарии к посту'))
    text = models.TextField(_('текст комментария'))
    rating = models.IntegerField(_('рейтинг комментария'), default=0)
    inverted_rating = models.IntegerField(_('рейтинг комментария'), default=0, editable=False)
    node_order_by = ('inverted_rating',)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.inverted_rating = -self.rating
        super().save(*args, **kwargs)

    def get_comments_deeper_from_node(self):
        serializer_class = create_comment_node_serializer(self.__class__)
        return serializer_class(self).data

    def add_point(self):
        self.point_operation(self, '+')

    def cut_point(self):
        self.point_operation(self, '-')

    @staticmethod
    def point_operation(instance, operand: str):
        operations = {
            '+': lambda x: x + 1,
            '-': lambda x: x - 1,
        }
        instance.rating = operations[operand](instance.rating)
        instance.save()
