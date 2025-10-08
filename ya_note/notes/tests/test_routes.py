from http import HTTPStatus

from django.contrib.auth import get_user_model

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

    def test_page_available_for_authorized_user(self):
        urls = [
            self.list_url,
            self.success_url,
            self.add_url,
        ]
        for url in urls:
            with self.subTest(name=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        urls = [
            self.edit_url,
            self.delete_url,
            self.detail_url,
        ]
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in urls:
                with self.subTest(user=user, name=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = [
            self.edit_url,
            self.delete_url,
            self.detail_url,
            self.list_url,
            self.success_url,
            self.add_url,
        ]
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
