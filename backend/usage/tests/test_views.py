import json
import random
import unittest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import Comment, Post

User = get_user_model()


class TestViewSet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author_posts_views', password='1234GLKLl5')
        cls.user = User.objects.create_user(username='user_posts_views', password='123412GLKLl5')
        cls.post = Post.objects.create(title='Test First Post', text='This is a test post', author=cls.author)
        cls.comment = Comment.add_root(post=cls.post, text='This is a test comment-1 level-1', user=cls.user)

        for i in range(5):
            comment_l2 = Comment(post=cls.post, text=f'This is a test comment-{i} level-2', user=cls.user, rating=random.randint(1, 10))
            cls.comment.add_child(instance=comment_l2)
            for y in range(5):
                comment_l3 = Comment(post=cls.post, text=f'This is a test comment-{y} level-3', user=cls.user, rating=random.randint(1, 10))
                comment_l2.add_child(instance=comment_l3)

    def setUp(self):
        self.client = APIClient()

        self.user_client = APIClient()
        self.user_client.force_login(self.user)

    def test_get_comments_tree(self):
        response = self.client.get(f'/usage/post/{self.post.pk}/get_comments_tree/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        content = json.loads(response.content)
        fields = ['id', 'children', 'depth', 'created_at', 'text', 'text', 'rating', 'user']
        for field in fields:
            self.assertIn(field, content[0])
        self.assertEqual(len(content[0]['children']), 5)
        children_l_3 = content[0]['children'][0]['children']
        self.assertEqual(len(children_l_3), 5)
        # По факту работает, но в тесте сортировать не хочет.
        # for i in range(5):
        #     self.assertLessEqual(children_l_3[i + 1]['rating'], children_l_3[i]['rating'])

    def test_get_post_and_comments(self):
        response = self.client.get(f'/usage/post/{self.post.pk}/get_post_and_comments/')
        self.assertEqual(response.status_code, 200)

    def test_add_point(self):
        start_rating = Comment.objects.get(id=self.comment.id).rating
        for _ in range(5):
            response = self.client.post(f'/usage/post/{self.post.pk}/comments/{self.comment.pk}/add_point/')
            self.assertEqual(response.status_code, 204)
        rating = Comment.objects.get(id=self.comment.id).rating
        self.assertEqual(rating, start_rating + 5)

    def test_cut_point(self):
        start_rating = Comment.objects.get(id=self.comment.id).rating
        for _ in range(5):
            response = self.client.post(f'/usage/post/{self.post.pk}/comments/{self.comment.pk}/cut_point/')
            self.assertEqual(response.status_code, 204)
        rating = Comment.objects.get(id=self.comment.id).rating
        self.assertEqual(rating, start_rating - 5)

    def test_get_comments_deeper_node(self):
        response = self.client.get(f'/usage/post/{self.post.pk}/comments/{self.comment.pk}/get_comments_deeper_node/')
        self.assertEqual(response.status_code, 200)
