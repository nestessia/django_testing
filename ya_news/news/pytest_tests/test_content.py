from http import HTTPStatus
from django.urls import reverse
import pytest
from django.test import Client
from news.models import Comment, News
from django.contrib.auth.models import User
import datetime


@pytest.fixture
def create_news():
    def _create_news(title, text):
        return News.objects.create(title=title, text=text)

    return _create_news


@pytest.mark.django_db
def test_10_news(create_news):
    """Проверка, что домашняя страница отображает до 10 новостей."""
    MAX_LENGHT = 10
    for i in range(11):
        create_news(f'News {i}', f'Text {i}')
    client = Client()
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['context']) == MAX_LENGHT


@pytest.mark.django_db
def test_sorted_news(create_news):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка."""
    news_3 = create_news('Title 3', 'Text 3')
    news_2 = create_news('Title 2', 'Text 2')
    news_1 = create_news('Title 1', 'Text 1')
    client = Client()
    response = client.get(reverse('news:home'))
    context = response.context['context']
    assert context[0] == news_3
    assert context[1] == news_2
    assert context[2] == news_1


@pytest.mark.django_db
def test_sorted_comments(create_news):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце."""
    news = create_news('Title', 'Text')
    user = User.objects.create_user(username='name',
                                    password='password')
    client = Client()
    client.login(username='name', password='password')
    comment_1 = Comment.objects.create(
        news=news, text='Comment 1',
        created=datetime.datetime(2023, 1, 1, 12, 0, 0), author=user)
    comment_2 = Comment.objects.create(
        news=news, text='Comment 2',
        created=datetime.datetime(2023, 1, 2, 12, 0, 0), author=user)
    comment_3 = Comment.objects.create(
        news=news, text='Comment 3',
        created=datetime.datetime(2023, 1, 3, 12, 0, 0), author=user)
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    context = response.context['news'].comment_set.all()
    assert [context[0], context[1], context[2]] == [comment_1, comment_2,
                                                    comment_3]


@pytest.mark.django_db
def test_comment_form_not_accessible_to_anonymous_user(create_news):
    """Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости."""
    news = create_news('Title', 'Text')
    client = Client()
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_accessible_to_authenticated_user(create_news):
    """Авторизованному пользователю доступна форма для отправки комментария
    на странице отдельной новости."""
    User.objects.create_user(username='user', password='password')
    news = create_news('Title', 'Text')
    client = Client()
    client.login(username='user', password='password')
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
