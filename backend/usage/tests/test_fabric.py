from django.contrib.auth import get_user_model
from django.test import TestCase
from publications.serializers import (create_comment_node_serializer,
                                      create_post_comment_serializer)

from ..models import Comment, Post

User = get_user_model()


class PostCommentSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(title='Test Post', text='This is a test post.', author=self.user)
        self.comment = Comment.add_root(user=self.user, post=self.post, text="Test Comment")

    def test_create_post_comment_serializer(self):
        serializer_class = create_post_comment_serializer(Post)
        serializer = serializer_class(instance=self.post)
        self.assertIsNotNone(serializer.data)

    def test_get_post_with_comments(self):
        data = self.post.get_post_with_comments()
        self.assertIn('title', data)
        self.assertIn('text', data)
        self.assertIn('comments', data)


class CommentSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='commentuser', password='12345')
        self.post = Post.objects.create(title='Test Post', text='This is a test post.', author=self.user)
        self.comment = Comment.add_root(user=self.user, post=self.post, text="Test Comment")

    def test_create_comment_node_serializer(self):
        serializer_class = create_comment_node_serializer(Comment)
        serializer = serializer_class(instance=self.comment)
        self.assertIsNotNone(serializer.data)

    def test_get_comments_deeper_from_node(self):
        data = self.comment.get_comments_deeper_from_node()
        self.assertIsNotNone(data)
