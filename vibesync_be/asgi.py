import os
import django

# Set default settings module before importing Django components
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibesync_be.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from room.routing import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from channels.exceptions import DenyConnection
import logging

logger = logging.getLogger(__name__)

# Set default settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibesync_be.settings') 
print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))
# Initialize Django application
django_asgi_app = get_asgi_application()




# Define ProtocolTypeRouter with HTTP and WebSocket support
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})