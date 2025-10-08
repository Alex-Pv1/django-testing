from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


COMMENT_DATA = {
    'text': 'Новый текст комментария',
}


def test_anonymous_user_cant_create_comment(client,
                                            news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comment_count = Comment.objects.count()
    client.post(news_detail_url, data=COMMENT_DATA)
    assert Comment.objects.count() == comment_count


def test_user_can_create_comment(author_client,
                                 author,
                                 news_detail_url,
                                 news):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    comment_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=COMMENT_DATA)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comment_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == COMMENT_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, news_detail_url):
    """Если комментарий содержит запрещённые слова,он не будет опубликован.
    Форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comment_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=bad_words_data)
    assert Comment.objects.count() == comment_count
    assert response.context['form'].errors['text'] == [WARNING]


def test_author_can_edit_comment(author_client,
                                 news_detail_url,
                                 news_edit_url,
                                 news,
                                 author,
                                 comment):
    """Авторизованный пользователь может редактироватьсвои комментарии."""
    comment_count = Comment.objects.count()
    response = author_client.post(news_edit_url, data=COMMENT_DATA)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert comment_count == Comment.objects.count()
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == COMMENT_DATA['text']
    assert edited_comment.author == comment.author
    assert edited_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                news_edit_url,
                                                news,
                                                comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(news_edit_url, data=COMMENT_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_new = Comment.objects.get(id=comment.id)
    assert comment_new.text == comment.text
    assert comment_new.author == comment.author
    assert comment_new.news == comment.news


def test_author_can_delete_comment(author_client,
                                   news_delete_url,
                                   news_detail_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comment_count = Comment.objects.count()
    response = author_client.post(news_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comment_count - 1


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  news_delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comment_count = Comment.objects.count()
    response = not_author_client.post(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count
