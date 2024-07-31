import os
import pika


class Client:
    queue_a_name = os.getenv('QUEUE_A_NAME', 'queue_a')
    queue_b_name = os.getenv('QUEUE_B_NAME', 'queue_b')
    def __init__(self, queue_name):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel_a = self.connection.channel()
        self.channel_a.queue_declare(queue=self.queue_a_name, durable=True, exclusive=False, auto_delete=False)
        self.channel_b = self.connection.channel()
        self.channel_b.queue_declare(queue=self.queue_b_name, durable=True, exclusive=False, auto_delete=False)
        self.consumer_tag = 'worker_a'

    def consume(self, callback, auto_ack=False, max_messages=1):
        self.channel_a.basic_qos(prefetch_count=max_messages, global_qos=False)
        self.channel_a.basic_consume(queue=self.queue_a_name, on_message_callback=callback, auto_ack=auto_ack, consumer_tag=self.consumer_tag)
        self.channel_a.start_consuming()

    def publish(self, message):
        pass

    def close(self):
        self.connection.close()
