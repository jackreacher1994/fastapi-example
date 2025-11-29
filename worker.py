from models import FileCreate
from celery import Celery

from config import settings
from websocket import socket_manager

celery = Celery(__name__)
celery.conf.broker_url = settings.celery_broker_url
celery.conf.result_backend = settings.celery_result_backend

@celery.task(name="upload_task")
def upload_task(client_id: str, files: list[dict]):
    websocket = socket_manager.get(client_id)
    if websocket is not None:
        socket_manager.send(websocket, {"message": "Task completed"})
    return True