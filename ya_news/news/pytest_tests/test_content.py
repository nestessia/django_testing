from http import HTTPStatus
from django.urls import reverse
import pytest
from django.test import Client
from django.contrib.auth.models import User
from yanews import settings
from news.models import Comment


@pytest.mark.django_db
def test_news(news):
    """Проверка, что домашняя страница отображает до 10 новостей."""
    for i in range(11):
        news()
    client = Client()
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['context']) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorted_news(news):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка."""
    news_3 = news()
    news_2 = news()
    news_1 = news()
    client = Client()
    response = client.get(reverse('news:home'))
    context = response.context['context']
    assert context[0] == news_3
    assert context[1] == news_2
    assert context[2] == news_1


@pytest.mark.django_db
def test_sorted_comments(news, comment):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце."""
    news = news()
    user = User.objects.create_user(username='name',
                                    password='password')
    client = Client()
    client.login(username='name', password='password')
    comment_1 = Comment.objects.create(news=news, text='Comment 1',
                                       author=user)
    comment_2 = Comment.objects.create( 
        news=news, text='Comment 2', author=user)
    comment_3 = Comment.objects.create(news=news, text='Comment 3',
                                       author=user)
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    context = response.context['news'].comment_set.all()
    assert [context[0], context[1], context[2]] == [comment_1, comment_2,
                                                    comment_3]


@pytest.mark.django_db
def test_comment_form_not_accessible_to_anonymous_user(news):
    """Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости."""
    news = news()
    client = Client()
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_accessible_to_authenticated_user(news):
    """Авторизованному пользователю доступна форма для отправки комментария
    на странице отдельной новости."""
    User.objects.create_user(username='NAME', password='PASSWORD')
    news = news()
    client = Client()
    client.login(username='NAME', password='PASSWORD')
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
