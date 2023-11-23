import asyncio

from aio_pika import (
    DeliveryMode,
    ExchangeType,
    IncomingMessage,
    Message,
    connect,
    connect_robust,
)
from aio_pika.abc import AbstractRobustConnection
from aiormq import AMQPConnectionError
from app.schemas import settings


class RabbitMQ:
    """Клиент RabbitMQ"""

    def __init__(self, process_callable) -> None:
        asyncio.run(self.initialization(process_callable))

    async def initialization(self, process_callable) -> None:
        """Инициализация клиента и конфигурирование очереди и распределителя на сервере"""
        self.publish_queue_name = str(settings.rabbit.RABBIT_QUEUE)
        self.exchange_name = str(settings.rabbit.RABBIT_EXCHANGE)
        try:
            self.connection = await connect(str(settings.rabbit.RABBIT_URL))
        except AMQPConnectionError:
            raise ConnectionError(
                f"Проблемы с подключением к RabbitMQ по адресу {str(settings.rabbit.RABBIT_URL)}, проверьте адрес или доступность сервера"
            )

        async with self.connection:
            self.channel = await self.connection.channel()
            self.publish_queue = await self.channel.declare_queue(
                name=self.publish_queue_name
            )
            self.exchange = await self.channel.declare_exchange(
                name=self.exchange_name, type=ExchangeType.FANOUT
            )
            await self.publish_queue.bind(self.exchange)
        self.response = None
        self.process_callable = process_callable

    async def consume(self, loop) -> AbstractRobustConnection:
        """Запуск в цикле функции, принимающей сообщения от RabbitMQ"""
        connection = await connect_robust(str(settings.rabbit.RABBIT_URL), loop=loop)
        channel = await connection.channel()
        queue = await channel.declare_queue(str(settings.rabbit.RABBIT_QUEUE))
        await queue.consume(self.process_incoming_message, no_ack=False)
        return connection

    async def process_incoming_message(self, message: IncomingMessage):
        """Функция обработки входящих сообщений"""
        await message.ack()
        body = message.body
        if body:
            self.process_callable(body.decode("utf-8"))

    async def send_message(self, message: dict):
        """Метод отправки сообщения в RabbitMQ"""
        m = Message(str(message).encode("utf-8"), delivery_mode=DeliveryMode.PERSISTENT)
        connection = await connect(str(settings.rabbit.RABBIT_URL))
        channel = await connection.channel()
        exchange = await channel.get_exchange(name=self.exchange_name)
        await exchange.publish(message=m, routing_key="BAUM")
