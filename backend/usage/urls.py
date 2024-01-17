from django.urls import include, path
from usage import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('post', views.PostViewSet, basename='post')
router.register(r'post/(?P<post_id>\d+)/comments', views.CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
]
