from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def users_login_url():
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    return reverse('users:logout')


@pytest.fixture
def users_signup_url():
    return reverse('users:signup')


@pytest.fixture
def news_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def redirect_edit_url(users_login_url, news_edit_url):
    return f'{users_login_url}?next={news_edit_url}'


@pytest.fixture
def redirect_delete_url(users_login_url, news_delete_url):
    return f'{users_login_url}?next={news_delete_url}'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def create_news_test():
    today = datetime.today()
    all_news = [News(title=f'Тестовая новость {index}',
                     text='Просто текст.',
                     date=today - timedelta(days=index)
                     )
                for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
                ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news():
    news = News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def create_new_comment(author, news):
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        # Создаем комментарий с обязательными полями
        comment = Comment(
            text=f'Комментарий {index}',
            news=news,
            author=author
        )
        # Сохраняем для получения id
        comment.save()
        # ПЕРЕЗАПИСЫВАЕМ поле created
        comment.created = today - timedelta(days=index)
        # Сохраняем с новой датой
        comment.save()
