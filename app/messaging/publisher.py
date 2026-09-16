import json 
import pika 
from app.config import settings 
from app.messaging.rabbitmq import setup_rabbitmq

def send_process_payment_message(payment_id: str): 
    params = pika.URLParameters(settings.rabbitmq_url) 
    connection = pika.BlockingConnection(params) 
    channel = connection.channel() 

    try: 
        channel.confirm_delivery() 

        setup_rabbitmq(channel) 

        channel.basic_publish( 
            exchange="payments", 
            routing_key="payment.created", 
            body=json.dumps({ 
                "payment_id": payment_id, 
                "retry_count": 0 }), 
            properties=pika.BasicProperties( delivery_mode=pika.DeliveryMode.Persistent ) ) 

    finally: connection.close()