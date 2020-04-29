import pytest

from search_service.settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB
from search_service.db import db, Query, Article, get_query_id, get_articles_from_db, save_articles_into_db


pytestmark = pytest.mark.asyncio


async def test_db():
    db_url = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'
    await db.set_bind(db_url)
    await db.gino.create_all()

    articles_to_save = [
        {'title': 'Nelson Mandela', 'url': 'https://en.wikipedia.org/wiki/Nelson_Mandela'},
        {'title': 'Mandela', 'url': 'https://en.wikipedia.org/wiki/Mandela'},
        {'title': 'Mandela', 'url': 'https://en.wikipedia.org/wiki/Mandela'},
        {'title': 'Mandela', 'url': 'https://en.wikipedia.org/wiki/Mandela'}
    ]
    await save_articles_into_db('Mandela', articles_to_save)
    articles = await Article.query.gino.all()
    assert len(articles) == 2
    query_id = await get_query_id('Mandela')
    articles = await get_articles_from_db(query_id)
    assert articles == [
        {'title': 'Nelson Mandela', 'url': 'https://en.wikipedia.org/wiki/Nelson_Mandela'},
        {'title': 'Mandela', 'url': 'https://en.wikipedia.org/wiki/Mandela'}
    ]

    await save_articles_into_db('Nelson', articles_to_save)
    query_id = await get_query_id('Nelson')
    articles = await get_articles_from_db(query_id)
    assert articles == [
        {'title': 'Nelson Mandela', 'url': 'https://en.wikipedia.org/wiki/Nelson_Mandela'},
        {'title': 'Mandela', 'url': 'https://en.wikipedia.org/wiki/Mandela'}
    ]
    articles = await Article.query.gino.all()
    assert len(articles) == 2
    queries = await Query.query.gino.all()
    assert len(queries) == 2

    await save_articles_into_db('Antonio', [])
    query_id = await get_query_id('Antonio')
    articles = await get_articles_from_db(query_id)
    assert articles == []

    articles = await Article.query.gino.all()
    assert len(articles) == 2
    queries = await Query.query.gino.all()
    assert len(queries) == 3

    await db.gino.drop_all()
    await db.pop_bind().close()
