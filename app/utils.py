import asyncio
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy import select
from .init_db import Base
from .db import SessionLocal, engine
from .model import Lines, RabbitMQ
from .schemas import CheckLine, settings

rabbit = RabbitMQ(str(settings.rabbit.RABBIT_URL))
all_cnt = 0
lim = 10

def create_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(engine)
        
def settings_rabbit():
    rabbit.create_queue('BAUM')
    rabbit.create_exchange('BAUM', 'BAUM')

def push_message(message):
    rabbit.send_message(message)

async def send_file(file: UploadFile):
    with file.file as f:
        f = f.read().decode("utf-8").split("\n")
        title = None
        for line in f:
            if title is None:
                title = line.strip()
            message = {'datetime': datetime.now().isoformat(),
                       'title': title,
                       'text': line.strip().replace('\xa0', ' '),
                       }
            push_message(str(message))
            await asyncio.sleep(3)

def valid_and_save(rmq_messages: list):
    if rmq_messages:
        # for m in rmq_messages:
            # print(Lines(m).__dict__)
        with SessionLocal() as session:
            session.add_all([Lines(m) for m in rmq_messages])
            session.commit()
            
def read_messages():
    rabbit.get_messages(queue_name='BAUM', func=valid_and_save)
    # while True:
    #     rmq_messages = rabbit.get_messages(queue_name='BAUM', count=10)
    #     valid_and_save(rmq_messages)

# def sync_async_callback():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(read_messages())
#     loop.close()
# def async_validate_and_save(channel, method_frame, header_frame, body):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(validate_and_save(channel, method_frame, header_frame, body))
#     loop.close()

def valid_and_save(channel, method_frame, header_frame, body):
    body_str = eval(body.decode("utf-8"))
    validate_body = CheckLine(**body_str)
    # new_line = Lines(**validate_body)
    
    with SessionLocal() as session:
        
        session.add(Lines(validate_body))
        # print(f'READ -- 123{validate_body}')
        session.commit()
#     channel.basic_ack(delivery_tag=method_frame.delivery_tag)

