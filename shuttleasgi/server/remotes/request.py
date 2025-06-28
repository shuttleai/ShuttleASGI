from shuttleasgi.messages import Request
from contextvars import ContextVar, Token
import uuid_utils as uuid

# TODO - move
_request_scope_context_storage: ContextVar[str] = ContextVar("shuttle_request_id")

class RequestIDMiddleware:
    def __init__(self, header_name: bytes = b"X-Request-ID") -> None:
        self.header_name = header_name
        self.prefix = "req_"

    async def __call__(self, request: Request, handler):
        value: str = self.prefix + uuid.uuid4().hex
        token: Token = _request_scope_context_storage.set(value)

        try:
            response = await handler(request)
        finally:
            _request_scope_context_storage.reset(token)

        response.add_header(self.header_name, value.encode("ascii"))
        return response

# TODO - move
# Accessing request id as string anywhere else:
def get_request_id() -> str | None:
    try:
        return _request_scope_context_storage.get()
    except LookupError:
        return None
