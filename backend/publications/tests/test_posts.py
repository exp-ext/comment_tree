import unittest

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from publications.models import Comment, Post
from publications.serializers import PostCommentSerializer, PostSerializer
from publications.views import PostViewSet
from rest_framework.test import APIClient

User = get_user_model()


class TestPostViewSet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='author_posts_views',
            password='1234GLKLl5',
            email='admin@admin.py'
        )
        cls.user = User.objects.create_user(
            username='user_posts_views',
            password='123412GLKLl5',
            email='no_admin@no_admin.py'
        )
        cls.first_post = Post.objects.create(title='Test First Post', text='This is a test post', author=cls.author)
        cls.viewset_get_comments = PostViewSet.as_view({'get': 'get_comments_tree'})

    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()

    def test_get_comments_tree(self):
        request = self.factory.get('/publications/post/1/get_comments_tree/')
        response = self.viewset(request, pk=self.post.pk)
        self.assertEqual(response.status_code, 200)

    def test_post_serializer(self):
        serializer = PostSerializer(instance=self.post)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['content'], 'This is a test post')

    def test_post_comment_serializer(self):
        comment1 = Comment.objects.create(post=self.post, text='Comment 1', depth=1)
        comment2 = Comment.objects.create(post=self.post, text='Comment 2', depth=1)

        serializer = PostCommentSerializer(instance=self.post)
        data = serializer.data

        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['content'], 'This is a test post')
        self.assertEqual(len(data['comments']), 2)
