from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node
from django.dispatch import receiver

from publications.serializers import CommentNodeSerializer, PostCommentSerializer

User = get_user_model()


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(_('заголовок поста'), max_length=80, unique=True)
    text = models.TextField(_('текст поста'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('автор'))

    class Meta:
        verbose_name = _('пост')
        verbose_name_plural = _('посты')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title

    def get_post_with_comments(self):
        return PostCommentSerializer(self)

    def get_comments_tree(self):
        comments = self.comments.filter(depth=1)
        return CommentNodeSerializer(comments, many=True)


class Comment(MP_Node):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('автор комментария'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('комментарии к посту'))
    text = models.TextField(_('текст комментария'))
    rating = models.IntegerField(_('рейтинг комментария'), default=0)
    inverted_rating = models.IntegerField(_('рейтинг комментария'), default=0, editable=False)
    node_order_by = ('inverted_rating',)

    class Meta:
        verbose_name = _('комментарий')
        verbose_name_plural = _('комментарии')

    def __str__(self) -> str:
        return self.text

    def get_comments_tree(self):
        return CommentNodeSerializer(self, many=True)

    def get_comments_by_node(self):
        return CommentNodeSerializer(self)

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


@receiver(pre_save, sender=Comment)
def pre_save_group(sender, instance, *args, **kwargs):
    instance.inverted_rating = -instance.rating
