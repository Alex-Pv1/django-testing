from notes.forms import NoteForm
from .base import TestBase


class TestNotesPage(TestBase):

    def test_author_notes_list(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_reader_context_list(self):
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)


class TestAddAndEditPage(TestBase):

    def test_form(self):
        urls_to_test = [
            self.add_url,
            self.edit_url,
        ]
        for args in urls_to_test:
            with self.subTest(name=args):
                response = self.author_client.get(args)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
