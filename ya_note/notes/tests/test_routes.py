from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class NoteTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.note = Note.objects.create(title='Test Note',
                                        text='Test Note Text',
                                        author=self.user)

    def test_anonymous_user_can_access_home_page(self):
        """
        Проверка, что анонимный пользователь может
        получить доступ к домашней странице.
        """
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_can_access_notes_pages(self):
        """
        Проверка, что аутентифицированный пользователь может
        получить доступ к страницам заметок.
        """
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirected_to_login_page(self):
        """
        Проверка, что анонимный пользователь
        перенаправляется на страницу входа.
        """
        login_url = reverse('users:login') + '?next='

        response = self.client.get(reverse('notes:list'))
        self.assertRedirects(response, login_url + reverse('notes:list'))

        response = self.client.get(reverse('notes:add'))
        self.assertRedirects(response, login_url + reverse('notes:add'))

        response = self.client.get(reverse('notes:success'))
        self.assertRedirects(response, login_url + reverse('notes:success'))

        response = self.client.get(
            reverse('notes:detail', args=[self.note.slug]))
        self.assertRedirects(response, login_url + reverse(
            'notes:detail', args=[self.note.slug]))

        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug]))
        self.assertRedirects(response, login_url + reverse('notes:edit', args=[
            self.note.slug]))

        response = self.client.get(
            reverse('notes:delete', args=[self.note.slug]))
        self.assertRedirects(response, login_url + reverse(
            'notes:delete', args=[self.note.slug]))

    def test_note_detail_page_redirects_to_login_for_unauthorized_user(self):
        """
        Проверка, что страница с подробностями заметки
        перенаправляет на страницу входа для неавторизованного пользователя.
        """

        note = Note.objects.create(title='Another Note',
                                   text='Another Note Text',
                                   author=User.objects.create_user(
                                       username='anotheruser',
                                       password='testpassword'))
        login_url = reverse('users:login') + '?next='
        response = self.client.get(reverse('notes:detail', args=[note.slug]))
        self.assertRedirects(response, login_url + reverse('notes:detail',
                                                           args=[note.slug]))
