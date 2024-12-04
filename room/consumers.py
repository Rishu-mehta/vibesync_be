from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.db import models
from asgiref.sync import sync_to_async
import logging
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from channels.exceptions import DenyConnection
import json


logger = logging.getLogger(__name__)

class RoomConsumer(AsyncWebsocketConsumer):
    connected_users = {}
    async def connect(self):
        logger.info("WebSocket connection attempt.")
        self.scope['user'] = None
        token = None

        try:
            # Extract token from query string
            query_string = self.scope.get('query_string', b'').decode()
            logger.debug(f"Query string received: {query_string}")
            token = query_string.split("token=")[-1]
            logger.debug(f"Extracted token: {token}")
        except Exception as e:
            logger.error(f"Error extracting token: {e}")
            await self.close(code=4001)
            return

        if token:
            try:
                # Authenticate token
                validated_token = JWTAuthentication().get_validated_token(token)
                user = await self.get_user_from_token(validated_token)
                self.scope['user'] = user
                logger.info(f"User authenticated: {user.username}")
            except AuthenticationFailed as e:
                logger.warning(f"Authentication failed: {e}")
                await self.close(code=4001)
                return
            except Exception as e:
                logger.error(f"Unexpected error during authentication: {e}")
                await self.close(code=4002)
                return

        if self.scope['user'] and self.scope['user'].is_authenticated:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'room_{self.room_name}'
            self.user = self.scope['user']
            
            # Initialize room in connected_users if not exists
            if self.room_group_name not in self.connected_users:
                self.connected_users[self.room_group_name] = set()
            
            # Add user to connected users
            self.connected_users[self.room_group_name].add(self.user.username)
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            logger.info(f"User {self.user.username} joined room: {self.room_name}")
            await self.accept()
            
            # Get list of connected users
            connected_users_list = list(self.connected_users[self.room_group_name])
            logger.info(f"Connected users in room {self.room_name}: {connected_users_list}")
            
            # Notify everyone about the current user list
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_list_update',
                    'users': connected_users_list,
                    'action': 'join',
                    'username': self.user.username
                }
            )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Remove user from connected users
            if self.room_group_name in self.connected_users:
                self.connected_users[self.room_group_name].remove(self.user.username)
                
                # Clean up empty rooms
                if not self.connected_users[self.room_group_name]:
                    del self.connected_users[self.room_group_name]
            
            # Get updated list of connected users
            connected_users_list = list(self.connected_users.get(self.room_group_name, set()))
            
            # Notify others about user leaving and updated user list
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_list_update',
                    'users': connected_users_list,
                    'action': 'leave',
                    'username': self.user.username
                }
            )
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
        logger.info(f"WebSocket disconnected with code: {close_code}")
        logger.info(f"Remaining users in room {self.room_name}: {connected_users_list}")

    async def user_list_update(self, event):
        """Handle user list updates"""
        await self.send(text_data=json.dumps({
            'type': 'user_list_update',
            'users': event['users'],
            'action': event['action'],
            'username': event['username']
        }))

    async def receive(self, text_data):
        user = self.scope['user']
        if user.is_authenticated:
            logger.info(f"Message received from {user.username}: {text_data}")
            # Broadcast the message to everyone in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': text_data,
                    'username': user.username
                }
            )
        else:
            logger.warning("Unauthorized access to WebSocket.")
            await self.send(text_data="Unauthorized access!")

    async def chat_message(self, event):
        """Handle chat messages"""
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username']
        }))

    async def user_join(self, event):
        """Handle user join notifications"""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username']
        }))

    async def user_leave(self, event):
        """Handle user leave notifications"""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username']
        }))

    @sync_to_async
    def get_user_from_token(self, validated_token):
        return JWTAuthentication().get_user(validated_token)