from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base import TestBase

User = get_user_model()


class TestRoutes(TestBase):

    def test_pages_availability(self):
        urls = [
            self.home_url,
            self.login_url,
            self.signup_url,
        ]
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def page_available_for_authorized_user(self):
        urls = [
            self.list_url,
            self.success_url,
            self.add_url,
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        self.login_url
        urls = [
            self.edit_url,
            self.delete_url,
            self.detail_url,
            self.list_url,
            self.success_url,
            self.add_url,
        ]
        for args in urls:
            with self.subTest(name=args):
                redirect_url = f'{self.login_url}?next={args}'
                response = self.client.get(args)
                self.assertRedirects(response, redirect_url)
