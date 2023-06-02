from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class NoteCreationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')

    def test_logged_in_user_can_create_note(self):
        """
        Проверка, что залогиненный пользователь может создать заметку.
        """
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('notes:add'), data={
            'title': 'Название заметки',
            'text': 'Текст заметки',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_user_cannot_create_note(self):
        """
        Проверка, что анонимный пользователь не может создать заметку.
        """
        response = self.client.post(reverse('notes:add'), data={
            'title': 'Название заметки',
            'text': 'Текст заметки',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)


class NoteSlugTest(TestCase):
    def test_duplicate_slug_not_allowed(self):
        """
        Проверка, что невозможно создать две заметки с одинаковым slug.
        """
        user = User.objects.create_user(username='testuser',
                                        password='testpassword')

        note1 = Note.objects.create(title='Заметка 1',
                                    text='Текст заметки 1',
                                    author=user)
        note2 = Note.objects.create(title='Заметка 2',
                                    text='Текст заметки 2',
                                    author=user)

        self.assertNotEqual(note1.slug, note2.slug)


class NoteSlugGenerationTest(TestCase):
    def test_slug_auto_generation(self):
        """
        Проверка, что slug формируется автоматически,
        если не заполнен при создании заметки.
        """
        user = User.objects.create_user(username='testuser',
                                        password='testpassword')

        note = Note.objects.create(title='Название заметки',
                                   text='Текст заметки', author=user)

        self.assertIsNotNone(note.slug)


class NoteAuthorizationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1',
                                              password='testpassword1')
        self.user2 = User.objects.create_user(username='user2',
                                              password='testpassword2')
        self.note = Note.objects.create(title='Заметка',
                                        text='Текст заметки',
                                        author=self.user1)

    def test_user_can_edit_own_note(self):
        """
        Проверка, что пользователь может редактировать свою заметку.
        """
        self.client.login(username='user1', password='testpassword1')

        response = self.client.post(reverse('notes:edit',
                                            args=[self.note.slug]),
                                    data={
            'title': 'Новое название',
            'text': 'Новый текст',
        })

        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Новое название')

    def test_user_cannot_edit_other_user_note(self):
        """
        Проверка, что пользователь не может редактировать чужую заметку.
        """
        self.client.login(username='user2', password='testpassword2')

        response = self.client.post(reverse('notes:edit',
                                            args=[self.note.slug]),
                                    data={
            'title': 'Новое название',
            'text': 'Новый текст',
        })

        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, 'Новое название')

    def test_user_can_delete_own_note(self):
        """
        Проверка, что пользователь может удалить свою заметку.
        """
        self.client.login(username='user1', password='testpassword1')

        response = self.client.post(
            reverse('notes:delete', args=[self.note.slug]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cannot_delete_other_user_note(self):
        """
        Проверка, что пользователь не может удалить чужую заметку.
        """
        self.client.login(username='user2', password='testpassword2')

        response = self.client.post(
            reverse('notes:delete', args=[self.note.slug]))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)







