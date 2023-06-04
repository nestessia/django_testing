import pytest
from news.models import News, Comment
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def news():
    def _create_news():
        return News.objects.create(title='Title', text='Text')
    return _create_news


@pytest.fixture
def create_user():
    def _create_users():
        return User.objects.create_user(username='Username',
                                        password='password')
    return _create_users


@pytest.fixture
def comment():
    def _create_comment(username, password):
        return Comment.objects.create(news=News.objects.create(
            title='Title',
            text='Text'),
            author=User.objects.create(username=username, password=password))
    return _create_comment
