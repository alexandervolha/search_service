import json

from search_service.db import get_articles_from_db, get_query_id, save_articles_into_db
from search_service.utils import get_request


DOMAIN = 'en.wikipedia.org'
URL = f'https://{DOMAIN}/w/api.php'


class WikiParser:
    def __init__(self, kafka_producer, client_session):
        self.kafka_producer = kafka_producer
        self.client_session = client_session

    async def get_and_send_articles(self, input_msg):
        query_str = input_msg.value.decode('utf-8')
        articles = await self.get_articles(query_str)
        await self.kafka_producer.send('response_topic', value=bytes(json.dumps(articles), 'utf-8'), key=input_msg.key)

    async def get_articles(self, query_str):
        query_id = await get_query_id(query_str)
        if query_id:
            articles = await get_articles_from_db(query_id)
        else:
            articles = await self.get_articles_from_wiki(query_str)
            await save_articles_into_db(query_str, articles)
        return articles

    async def get_articles_from_wiki(self, query_str):
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query_str
        }
        response = await get_request(URL, params, self.client_session)
        return self.parse_response(response)

    @staticmethod
    def parse_response(response):
        result = []
        articles_data = response.get('query', {}).get('search', [])
        for article in articles_data:
            title = article['title']
            result.append({'title': title, 'url': f'https://{DOMAIN}/wiki/{title.replace(" ", "_")}'})
        return result
