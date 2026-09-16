from app.config import settings
import pika

RABBITMQ_URL = settings.rabbitmq_url

params = pika.URLParameters(RABBITMQ_URL)

def create_connection():
    return pika.BlockingConnection(params)

channel = create_connection().channel()

print("Connected to rabbitmq successfully")

channel.close()