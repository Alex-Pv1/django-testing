from notes.models import Note
from .base import TestBase


class TestNotesPage(TestBase):

    def test_notes_list(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        first_note = object_list[0]
        self.assertIn(first_note, object_list)

    def test_reader_context_list(self):
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, 0)

    def test_author_context_list(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, 5)


class TestAddAndEditPage(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.notes = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )

    def test_form(self):
        urls_to_test = [
            self.add_url,
            self.edit_url,
        ]
        for args in urls_to_test:
            with self.subTest(name=args):
                response = self.author_client.get(args)
                self.assertIn('form', response.context)
