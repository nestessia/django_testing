import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from news.forms import CommentForm
from news.models import Comment, News
from news.forms import BAD_WORDS, WARNING
from pytest_django.asserts import assertFormError
from random import choice


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(news):
    """
    Анонимный пользователь не может отправить комментарий.
    """
    client = Client()
    response = client.post(reverse('news:detail', kwargs={'pk': news().pk}))
    assert response.status_code == 302
    assert response.url.startswith(reverse('users:login'))


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(news):
    """
    Авторизованный пользователь может отправить комментарий.
    """
    User.objects.create_user(username='NAME', password='PASS')
    news = news()
    first_comment_count = Comment.objects.filter(news=news).count()
    client = Client()
    client.login(username='NAME', password='PASS')
    client.post(reverse('news:detail', kwargs={'pk': news.pk}),
                {'text': 'COMMENT TEXT'})
    second_comment_count = Comment.objects.filter(news=news).count()
    assert second_comment_count == first_comment_count + 1
    comment = Comment.objects.last()
    assert comment.news == news


@pytest.mark.django_db
def test_comment_with_bad_words_not_published(news):
    '''Если комментарий содержит запрещённые слова, он не будет
    опубликован, а форма вернёт ошибку.'''
    User.objects.create_user(username='USERNAME', password='PASSWORD')
    news = news()
    initial_comment_count = Comment.objects.filter(news=news).count()
    client = Client()
    client.login(username='USERNAME', password='PASSWORD')
    response = client.post(reverse('news:detail',
                           kwargs={'pk': news.pk}),
                           data={'text': choice(BAD_WORDS)})
    assert initial_comment_count == 0
    assertFormError(response, 'form', 'text', WARNING)


@pytest.mark.django_db
def test_authenticated_user_can_edit_or_delete_own_comments():
    '''
    Авторизованный пользователь может редактировать или удалять свои
    комментарии.
    '''
    user = User.objects.create_user(username='NAME', password='PASSWORD')
    User.objects.create_user(username='NAME2', password='PASSWORD2')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user,
                                     text='This is a comment')
    client = Client()
    client.login(username='NAME', password='PASSWORD')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 200
    client.login(username='NAME2', password='PASSWORD2')
    '''
    Авторизованный пользователь не может редактировать или удалять
    чужие комментарии.
    '''
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 404
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 404
