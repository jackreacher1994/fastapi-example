import json
from models import FileCreate
from celery import Celery
import asyncio

from config import settings
from websocket import socket_manager

celery = Celery(__name__)
celery.conf.broker_url = settings.celery_broker_url
celery.conf.result_backend = settings.celery_result_backend

@celery.task(name="upload_task")
def upload_task(client_id: str, files: list[dict]):
    # Run the async send in a new event loop since Celery tasks are sync
    asyncio.run(socket_manager.send(client_id, json.dumps({"message": "Task completed"})))
    return True