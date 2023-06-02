from http import HTTPStatus
from django.urls import reverse
import pytest
from django.test import Client
from news.models import Comment, News
from django.contrib.auth.models import User

@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    '''Главная страница доступна анонимному пользователю.'''
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anon_availability_for_detail_page(client):
    '''Страница отдельной новости доступна анонимному пользователю.'''
    news = News.objects.create(title='Title', text='Text')
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_author_can_delete_news(client):
    '''Страница удаления комментария доступна автору комментария.'''
    user = User.objects.create_user(username='name',
                                    password='password')
    news = News.objects.create(title='Title', text='Text')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Text')
    client = Client()
    client.login(username='name', password='password')
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_author_can_edit_news(client):
    '''Страница редактирования комментария доступна автору комментария.'''
    user = User.objects.create_user(username='name',
                                    password='password')
    news = News.objects.create(title='Title', text='Text')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Text')
    client = Client()
    client.login(username='name', password='password')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anon_redirect_after_edit_page(client):
    '''При попытке перейти на страницу редактирования комментария
    анонимный пользователь перенаправляется на страницу
    авторизации.'''
    user = User.objects.create_user(username='name',
                                    password='password')
    news = News.objects.create(title='Title', text='Text')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Text')
    client = Client()
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert response.url == '/auth/login/?next=' + reverse('news:edit',
                                                          kwargs={'pk': comment.pk})


@pytest.mark.django_db
def test_anon_redirect_after_delete_page(client):
    '''При попытке перейти на страницу удаления комментария
    анонимный пользователь перенаправляется на страницу
    авторизации.'''
    user = User.objects.create_user(username='name',
                                    password='password')
    news = News.objects.create(title='Title', text='Text')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Text')
    client = Client()
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert response.url == '/auth/login/?next=' + reverse('news:delete',
                                                          kwargs={'pk': comment.pk})


@pytest.mark.django_db
def test_anon_cant_go_to_edit_page_another_user(client):
    '''Авторизованный пользователь не может зайти на страницы редактирования
    чужих комментариев (возвращается ошибка 404).'''
    user = User.objects.create_user(username='name',
                                    password='password')
    news = News.objects.create(title='Title', text='Text')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Text')
    client = Client()
    client.login(username='user', password='pass')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert response.url == '/auth/login/?next=' + reverse('news:edit',
                                                          kwargs={'pk': comment.pk})
    

@pytest.mark.django_db
def test_anon_cant_go_to_delete_page_another_user(client):
    '''Авторизованный пользователь не может зайти на страницы редактирования
    чужих комментариев (возвращается ошибка 404).'''
    user = User.objects.create_user(username='name',
                                    password='password')
    news = News.objects.create(title='Title', text='Text')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Text')
    client = Client()
    client.login(username='user', password='pass')
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert response.url == '/auth/login/?next=' + reverse('news:delete',
                                                          kwargs={'pk': comment.pk})


@pytest.mark.django_db
def test_anon_can_go_to_login_sign_up_out_pages(client):
    '''Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.'''
    client = Client()
    response = client.get(reverse('users:signup'))
    assert response.status_code == 200
    response = client.get(reverse('users:login'))
    assert response.status_code == 200
    response = client.get(reverse('users:logout'), follow=True)
    assert response.status_code == 200

