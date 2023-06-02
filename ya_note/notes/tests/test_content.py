from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author2 = User.objects.create(username='Author2')
        cls.note = Note.objects.create(title='Title',
                                       text='Text',
                                       author=cls.author)
        cls.note2 = Note.objects.create(title='Title1',
                                        text='Text1',
                                        author=cls.author2)

    def test_list_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_list_unique(self):
        self.client.force_login(self.author)
        response = self.client.get(self.URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note2, object_list)

    def test_edit_has_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.id,))
        response = self.client.get(url)
        self.assertIn('True', response.context)

    def test_add_has_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
