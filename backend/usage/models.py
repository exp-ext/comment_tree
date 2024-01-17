from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from publications.models import AbstractComment, AbstractPost


User = get_user_model()


class Post(AbstractPost):
    title = models.CharField(_('заголовок поста'), max_length=80, unique=True)
    text = models.TextField(_('текст поста'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('автор'))

    class Meta:
        verbose_name = _('пост')
        verbose_name_plural = _('посты')

    def __str__(self) -> str:
        return self.title


class Comment(AbstractComment):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('автор комментария'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('комментарии к посту'))
    text = models.TextField(_('текст комментария'))
    rating = models.IntegerField(_('рейтинг комментария'), default=0)

    class Meta:
        verbose_name = _('комментарий')
        verbose_name_plural = _('комментарии')

    def __str__(self) -> str:
        return self.text
