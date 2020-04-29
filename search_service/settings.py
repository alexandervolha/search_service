import os


POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'kafka:9092')
GROUP_ID = os.getenv('GROUP_ID', 'search_group')
