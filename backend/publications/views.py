from publications.serializers import BlankSerializer
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from publications.models import Comment, Post
from publications.serializers import CommentRatingSerializer, CommentSerializer, PostSerializer, PostCommentSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=('get',))
    def get_comments_tree(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        instance = self.get_object()
        serializer = PostCommentSerializer(instance)
        return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    @staticmethod
    def point_operation(pk: str, operand: str):
        comment = get_object_or_404(Comment, id=pk)
        operations = {
            '+': lambda x: x + 1,
            '-': lambda x: x - 1,
        }
        comment.rating = operations[operand](comment.rating)
        comment.save()

    def get_serializer_class(self):
        """Получение класса сериализатора в зависимости от действия.

        ### Returns:
        - Serializer: Класс сериализатора.

        """
        if (self.action == 'add_point' or self.action == 'cut_point') and self.request.method == 'POST':
            return BlankSerializer
        return CommentSerializer

    def get_queryset(self) -> QuerySet:
        """Возвращает комментарий."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.all()

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
        self.point_operation(kwargs.get('pk'), '+')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post',))
    def cut_point(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.point_operation(kwargs.get('pk'), '-')
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=('get',))
    def get_comments_tree(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.filter(depth=1)
        serializer = CommentRatingSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
