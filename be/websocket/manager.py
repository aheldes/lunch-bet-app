import asyncio
import logging

import redis.asyncio as redis
from fastapi import WebSocket

logger = logging.getLogger("uvicorn.error")


class RedisPubSubManager:
    """Class for managing Redis Pub/Sub."""

    def __init__(self, host="localhost", port=6379):
        self.redis_host = host
        self.redis_port = port
        self.redis_connection = None
        self.pubsub = None

    async def connect(self) -> None:
        """Connect and initialize Redis Pub/Sub."""
        self.redis_connection = redis.Redis(host=self.redis_host, port=self.redis_port)
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, channel: str, message: str) -> None:
        """Publishes a message to a specific Redis channel."""
        logger.info("Publishing message - %s - to channel: %s", message, channel)
        await self.redis_connection.publish(channel, message)

    async def subscribe(self, channel: str):
        """Subscribes to a Redis channel."""
        logger.info("Subscribing to channel: %s", channel)
        await self.pubsub.subscribe(channel)

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribes from a Redis channel."""
        logger.info("Unsubscribing to channel: %s", channel)
        await self.pubsub.unsubscribe(channel)


class WebSocketManager:
    """Class to manage WebSocket connections."""

    def __init__(self) -> None:
        self.channels: dict[str, list[WebSocket]] = {}
        self.pubsub_client = RedisPubSubManager()

    async def create_channel(self, channel: str, websocket: WebSocket) -> None:
        """Creates a connection for a channel."""
        await websocket.accept()

        if channel in self.channels:
            self.channels[channel].append(websocket)
            return

        self.channels[channel] = [websocket]
        await self.pubsub_client.connect()
        await self.pubsub_client.subscribe(channel)
        asyncio.create_task(self._pubsub_data_reader())

    async def broadcast(self, channel: str, message: str) -> None:
        """Broadcasts a message to all connected sockets in a channel."""
        await self.pubsub_client.publish(channel, message)

    async def remove_user(self, channel: str, websocket: WebSocket) -> None:
        """Removes a user's WebSocket connection from a channel."""
        logger.info("Removing user from channel: %s", channel)
        if channel in self.channels and websocket in self.channels[channel]:
            logger.info("Socket found, removing.")
            self.channels[channel].remove(websocket)

            if not self.channels[channel]:
                logger.info(
                    "Socket was last in channel, removing channel and unsubscribing."
                )
                del self.channels[channel]
                await self.pubsub_client.unsubscribe(channel)

    async def _pubsub_data_reader(self) -> None:
        """Reads and processes messages received from Redis Pub/Sub."""
        pubsub = self.pubsub_client.pubsub
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if not message:
                continue

            channel = message["channel"].decode("utf-8")
            if channel not in self.channels:
                continue

            data = message["data"].decode("utf-8")
            all_sockets = self.channels[channel]
            for socket in all_sockets:
                await socket.send_text(data)
            await asyncio.sleep(0.01)


socket_manager = WebSocketManager()
