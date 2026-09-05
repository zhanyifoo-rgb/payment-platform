from app.main import channel

def send_process_payment_message(payment_id: str):
    # all payments are succeed for now
    channel.basic_publish(exchange='payments', routing_key='payment.created',body=payment_id)