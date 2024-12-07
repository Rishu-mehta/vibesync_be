1. clone repo
2. create virtual environment
3.activate venv
4.run migrations and migrate
5.run server
daphne -p 8000 --websocket_timeout 1200 vibesync_be.asgi:application