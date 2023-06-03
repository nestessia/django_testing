from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class NoteCreationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test',
                                             password='123')

    def test_logged_in_user_can_create_note(self):
        """
        Залогиненный пользователь может создать заметку.
        """
        add_url = reverse('notes:add')
        self.client.login(username='test', password='123')

        self.client.post(add_url, data={
            'title': 'Название заметки',
            'text': 'Текст заметки',
        })
        count = Note.objects.count()
        self.assertEqual(count, 1)

    def test_anonymous_user_cannot_create_note(self):
        """
        Анонимный пользователь не может создать заметку.
        """
        add_url = reverse('notes:add')
        self.client.post(add_url, data={
            'title': 'Название заметки',
            'text': 'Текст заметки',
        })

        count = Note.objects.count()
        self.assertEqual(count, 0)


class NoteSlugTest(TestCase):
    def test_duplicate_slug_not_allowed(self):
        """
        Невозможно создать две заметки с одинаковым slug.
        """
        user = User.objects.create_user(username='test',
                                        password='123')

        note1 = Note.objects.create(title='Заголовок 1',
                                    text='Текст 2',
                                    author=user)
        note2 = Note.objects.create(title='Заголовок 2',
                                    text='Текст 2',
                                    author=user)

        self.assertNotEqual(note1.slug, note2.slug)


class NoteSlugGenerationTest(TestCase):
    def test_slug_auto_generation(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически
        """
        user = User.objects.create_user(username='test',
                                        password='123')

        note = Note.objects.create(title='Заголовок',
                                   text='Текст', author=user)

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
        Пользователь может редактировать свою заметку.
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
        Пользователь не может редактировать чужую заметку.
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
        Пользователь может удалить свою заметку.
        """
        self.client.login(username='user1', password='testpassword1')

        response = self.client.post(
            reverse('notes:delete', args=[self.note.slug]))
        count = Note.objects.count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count, 0)

    def test_user_cannot_delete_other_user_note(self):
        """
        Пользователь не может удалить чужую заметку.
        """
        self.client.login(username='user2', password='testpassword2')

        response = self.client.post(
            reverse('notes:delete', args=[self.note.slug]))

        self.assertEqual(response.status_code, 404)
        count = Note.objects.count()
        self.assertEqual(count, 1)
