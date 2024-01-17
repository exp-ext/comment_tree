from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from usage.models import Comment, Post
from usage.serializers import (BlankSerializer, CommentSerializer,
                               PostSerializer)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=('get',))
    def get_post_and_comments(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        instance = self.get_object()
        return Response(instance.get_post_with_comments(), status=status.HTTP_200_OK)

    @action(detail=True, methods=('get',))
    def get_comments_tree(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        instance = self.get_object()
        return Response(instance.get_comments_tree(), status=status.HTTP_200_OK)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self) -> QuerySet:
        """Возвращает комментарий."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.all()

    def get_serializer_class(self):
        if (self.action == 'add_point' or self.action == 'cut_point') and self.request.method == 'POST':
            return BlankSerializer
        return CommentSerializer

    def perform_create(self, serializer: ModelSerializer) -> None:
        """Создаёт комментарий в БД."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        parent_node = serializer.validated_data.get('parent_node')
        comment = Comment(
            user=self.request.user,
            post=post,
            text=serializer.validated_data.get('text')
        )
        if not parent_node:
            Comment.add_root(instance=comment)
        else:
            parent_node = get_object_or_404(post.comments, id=parent_node)
            parent_node.add_child(instance=comment)

    @action(detail=True, methods=('post',))
    def add_point(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        comment = get_object_or_404(Comment, id=kwargs.get('pk'))
        comment.add_point()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post',))
    def cut_point(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        comment = get_object_or_404(Comment, id=kwargs.get('pk'))
        comment.cut_point()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('get',))
    def get_comments_deeper_node(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        return Response(comment.get_comments_deeper_from_node(), status=status.HTTP_200_OK)
