import django.contrib.auth.backends
import pytest
from channels.db import database_sync_to_async
from channels.testing import HttpCommunicator
from django.http import request
from django.test import Client
from channels.testing.websocket import WebsocketCommunicator
from djangoChannels1.asgi import application
import os
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.test import TestCase
from room.consumers import ChatConsumer

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@database_sync_to_async
def create_user(username, email, password):
    user = User(
        username=username,
        email=email,
        password=password
    ).save()
    return user


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def pytest_chat():
    client_1 = Client()
    client_2 = Client()
    user_1 = await create_user('test1', 'test1@gmail.com', 'qwerty0192')
    user_2 = await create_user('test2', 'test2@gmail.com', 'qwerty0192')
    client_1.force_login(user=user_1, backend=django.contrib.auth.backends.ModelBackend)
    client_2.force_login(user=user_2)
    communicator1 = WebsocketCommunicator(application=application, path='/ws/friends/', headers=[(
        b'cookie',
        f'sessionid={client_1.cookies["sessionid"].value}'.encode('ascii')
    )])
    connected = await communicator1.connect()
    assert connected

    await communicator1.send_json_to(
        {"message": "No message", "username": "axlrose023", "roomname": "Friends"})
    message = await communicator1.receive_json_from()
    assert message['message'] == 'No message'

@pytest.mark.asyncio
async def pytest_my_consumer():
    communicator = HttpCommunicator(ChatConsumer, "GET", "/rooms/")
    response = await communicator.get_response()
    assert response["body"] == b"test response"
    assert response["status"] == 200
