class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Perform JWT authentication
        # For example, extract the token from headers or query parameters
        headers = dict(scope.get("headers", []))
        token = headers.get(b"authorization", b"").decode("utf-8")

        if token:
            # Validate token (use your logic here)
            scope["user"] = await self.authenticate_token(token)
        else:
            scope["user"] = None

        # Pass control to the next middleware or app
        return await self.app(scope, receive, send)

    async def authenticate_token(self, token):
        # Implement your token validation logic
        # Return the user object or raise an exception if invalid
        pass
