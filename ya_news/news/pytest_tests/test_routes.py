from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db

CLIENT = lf('client')
NOT_AUTHOR_CLIENT = lf('not_author_client')
AUTHOR_CLIENT = lf('author_client')
COMMENT_EDIT = lf('news_edit_url')
COMMENT_DELETE = lf('news_delete_url')


@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    [
        (lf('home_url'), CLIENT, HTTPStatus.OK),
        (lf('news_detail_url'), CLIENT, HTTPStatus.OK),
        (lf('users_login_url'), CLIENT, HTTPStatus.OK),
        (lf('users_logout_url'), CLIENT, HTTPStatus.METHOD_NOT_ALLOWED),
        (lf('users_signup_url'), CLIENT, HTTPStatus.OK),
        (COMMENT_EDIT, CLIENT, HTTPStatus.FOUND),
        (COMMENT_DELETE, CLIENT, HTTPStatus.FOUND),
        (COMMENT_EDIT, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_DELETE, AUTHOR_CLIENT, HTTPStatus.OK),
    ],
)
def test_pages_availability(url, client_fixture, expected_status):
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, redirect_url',
    [
        (COMMENT_EDIT, lf('redirect_edit_url')),
        (COMMENT_DELETE, lf('redirect_delete_url')),
    ]
)
def test_redirect_for_anonymous_users(client, url, redirect_url):
    assertRedirects(client.get(url), redirect_url)
