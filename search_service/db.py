import logging
from contextlib import asynccontextmanager

import gino
from sqlalchemy.dialects.postgresql import insert
from asyncpg.exceptions import UniqueViolationError


from search_service.settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB
from search_service.utils import async_retry


db = gino.Gino()


class Query(db.Model):
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    query_str = db.Column(db.String, unique=True)


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    url = db.Column(db.String)


class QueryXArticle(db.Model):
    __tablename__ = 'queries_x_articles'

    query_id = db.Column(db.Integer, db.ForeignKey('queries.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    id = db.PrimaryKeyConstraint('query_id', 'article_id', name='qxa_pkey')


async def get_query_id(query_str):
    query_id = await Query.select('id').where(Query.query_str == query_str).gino.scalar()
    return query_id


async def get_articles_from_db(query_id):
    query = db.select([Article.title, Article.url])\
        .select_from(Query.join(QueryXArticle).join(Article)).where(QueryXArticle.query_id == query_id)
    articles = await query.gino.all()
    return [{'title': article.title, 'url': article.url} for article in articles]


async def save_articles_into_db(query_str, articles):
    async with db.transaction():
        query_id = (await Query.create(query_str=query_str)).id
        for article in articles:
            article_insert = insert(Article).values(title=article['title'], url=article['url'])
            article_insert = article_insert.on_conflict_do_update(
                index_elements=[Article.title], set_=dict(url=article_insert.excluded.url)
            ).returning(*[Article.id])
            article_id = (await article_insert.gino.model(Article).first()).id

            qxa_insert = insert(QueryXArticle).values(query_id=query_id, article_id=article_id)
            qxa_insert = qxa_insert.on_conflict_do_update(
                index_elements=[QueryXArticle.query_id, QueryXArticle.article_id],
                set_=dict(query_id=qxa_insert.excluded.query_id, article_id=qxa_insert.excluded.article_id)
            )
            await qxa_insert.gino.model(QueryXArticle).first()


@asynccontextmanager
async def configure_db():
    db_url = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'
    await async_retry()(db.set_bind)(db_url)
    try:
        try:
            await db.gino.create_all()
        except UniqueViolationError as e:
            logging.error(repr(e))
        finally:
            yield
    finally:
        await db.pop_bind().close()
