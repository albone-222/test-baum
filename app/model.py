import asyncio
from datetime import datetime
import traceback
import pika
from pika.exceptions import AMQPConnectionError, StreamLostError

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .schemas import CheckLine, settings, ExchangeType

from .db import Base, SessionLocal


class Lines(Base):
    # Модель таблицы БД с вопросами
    __tablename__ = "lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    datetime = mapped_column(DateTime)
    title: Mapped[str] = mapped_column(index=True)
    text: Mapped[str]
    x_in_line: Mapped[int]
    
    def __init__(self, data: CheckLine):
        # self.datetime = data['datetime']
        # self.title = data['title']
        # self.text = data['text']
        self.datetime = data.datetime
        self.title = data.title
        self.text = data.text
        self.x_count()
    
    def x_count(self):
        self.x_in_line = self.text.lower().count('х')

class RabbitMQ():
    url = None
    channel = None
    channel_receive = None
    default_exchange = None
    
    def __init__(self, url) -> None:
        self.url = url
    
    def get_channel(self) -> None:
        rmq_parameters = pika.URLParameters(self.url)
        try:
            rmq_connection = pika.BlockingConnection(rmq_parameters)
        except AMQPConnectionError:
            raise RuntimeError('Ошибка подключения к RabbitMQ')
        self.channel = rmq_connection.channel()
        self.channel_receive = rmq_connection.channel()
    
    def get_receive_channel(self) -> None:
        rmq_parameters = pika.URLParameters(self.url)
        try:
            rmq_connection = pika.BlockingConnection(rmq_parameters)
        except AMQPConnectionError:
            raise RuntimeError('Ошибка подключения к RabbitMQ')
        self.channel_receive = rmq_connection.channel()
    
    def send_message(self, message, routing_key:str='', exchange:str=None) -> None:
        self.get_channel()
        if exchange is None: exchange = self.default_exchange
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
        self.channel.close()
        
    def create_queue(self, queue_name:str, durable:bool = True) -> None:
        self.get_channel()
        self.channel.queue_declare(queue=queue_name, durable=durable)
        self.channel.close()
    
    def create_exchange(self, exchange_name:str, 
                        bind_queue: str, 
                        exchange_type:ExchangeType = 'fanout', 
                        routing_key:str = None, 
                        default:bool = True, 
                        durable:bool = True) -> None:
        self.get_channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)
        if default: self.default_exchange = exchange_name
        self.channel.queue_bind(exchange=exchange_name, queue=bind_queue, routing_key=routing_key)
        self.channel.close()
        
    def get_messages(self, queue_name:str, func):
        self.get_receive_channel()
        self.channel_receive.basic_consume(queue=queue_name, on_message_callback=func)
        try:
            self.channel_receive.start_consuming()
        except KeyboardInterrupt:
            self.channel_receive.stop_consuming()
        except Exception:
            self.channel_receive.stop_consuming()
            print("Ошибка:\n", traceback.format_exc())
        self.channel_receive.close()
        
    # def get_messages(self, queue_name:str, count:int):
    #     # self.get_receive_channel()
    #     # cnt = self.channel_receive.queue_declare(queue=queue_name, passive=True).method.message_count
    #     messages = []
    #     # print(cnt)
    #     while count > 0:
    #         message = self.get_message(queue_name=queue_name)
    #         if message is None:
    #             break
    #         else:
    #             messages.append(message)
    #             count -= 1
        
    #     if messages:
    #         messages = list(map(eval, messages))
    #     return messages
    #     # async with SessionLocal() as session:
    #     #     session.add_all([Lines(m) for m in messages])
    #     #     await session.commit()
            
    # def get_message(self, queue_name:str):
    #     self.get_receive_channel()
    #     try:
    #         method_frame, header_frame, body = self.channel_receive.basic_get(queue_name)
    #         if method_frame:
    #             self.channel_receive.basic_ack(method_frame.delivery_tag)
    #         self.channel_receive.close()
    #         return body
    #     except StreamLostError:
    #         print('Очередь пустая, ждем сообщения...')
    #         self.channel_receive.close()
    #         return None
    #     # if cnt > count:
    #     #     cnt = count
    #     # while cnt:
    #     #     method_frame, header_frame, body = self.channel_receive.basic_get(queue_name)
    #     #     print(body.decode("utf-8"))
    #     #     if method_frame:
    #     #         self.channel_receive.basic_ack(method_frame.delivery_tag)
    #     #     cnt -= 1