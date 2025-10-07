from http import HTTPStatus

from django.contrib.auth import get_user
from pytils.translit import slugify

from notes.models import Note
from .base import TestBase


class TestNoteCreation(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'text': 'Текст',
            'title': 'Заголовок'
        }

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        self.anonymous_client.post(self.add_url, data=self.form_data)
        final_notes_count = Note.objects.count()
        self.assertEqual(final_notes_count, notes_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        self.auth_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        user_from_client = get_user(self.auth_client)
        self.assertEqual(note.author, user_from_client)

    def test_two_identical_slug(self):
        existing_note = Note.objects.first()
        duplicate_form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': existing_note.slug
        }
        notes_count = Note.objects.count()
        response = self.auth_client.post(
            self.add_url,
            data=duplicate_form_data
        )
        notes_count_2 = Note.objects.count()
        self.assertEqual(notes_count_2, notes_count)
        self.assertFormError(
            response.context['form'],
            'slug',
            'note-0 - такой slug уже существует, '
            'придумайте уникальное значение!'
        )

    def test_automatic_creation_slug(self):
        Note.objects.all().delete()
        self.auth_client.post(self.add_url, data=self.form_data)
        note = Note.objects.latest('id')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestCommentEditDelete(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'text': 'Еще Текст',
            'title': 'Еще Заголовок',
            'slug': 'new-slug'
        }

    def test_user_cant_edit_note_of_another_user(self):
        original_note_id = self.note.id
        response = self.reader_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(pk=original_note_id)
        self.assertEqual(note_after.text, self.note.text)
        self.assertEqual(note_after.title, self.note.title)
        self.assertEqual(note_after.slug, self.note.slug)
        self.assertEqual(note_after.author, self.note.author)

    def test_author_can_edit_note(self):
        original_note_id = self.note.id
        response = self.author_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(pk=original_note_id)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_delete_note_of_another_user(self):
        notes_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        final_notes_count = Note.objects.count()
        self.assertEqual(final_notes_count, notes_count)

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        final_notes_count = Note.objects.count()
        self.assertEqual(final_notes_count, notes_count - 1)
