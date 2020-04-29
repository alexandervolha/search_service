import asyncio
import logging

import aiohttp

from search_service.db import configure_db
from search_service.kafka import AIOKafkaProducerCtx, AIOKafkaConsumerCtx
from search_service.settings import KAFKA_SERVER, GROUP_ID
from search_service.utils import setup_logging
from search_service.parser import WikiParser


async def main():
    setup_logging()
    logging.info('Waiting for kafka topics creation...')
    await asyncio.sleep(15)  # wait for topics creation
    logging.info('Search service started.')
    try:
        async with \
                aiohttp.ClientSession() as session, \
                AIOKafkaProducerCtx(bootstrap_servers=KAFKA_SERVER) as kafka_producer,\
                AIOKafkaConsumerCtx(
                    'request_topic', bootstrap_servers=KAFKA_SERVER, group_id=GROUP_ID
                ) as kafka_consumer,\
                configure_db():
            parser = WikiParser(kafka_producer, session)
            async for msg in kafka_consumer:
                logging.info(f'Got message, partition={msg.partition}')
                await parser.get_and_send_articles(msg)
    finally:
        logging.info('Search service stopped.')


if __name__ == '__main__':
    asyncio.run(main())
