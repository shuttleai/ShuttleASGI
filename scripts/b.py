import asyncio
from contextvars import ContextVar, Token
from typing import Awaitable, Callable

# ✅ Global request-scoped context store
_request_scope_context_storage: ContextVar[dict] = ContextVar("shuttle_context")

# ✅ UserDict-like context for plugin access
class RequestContext:
    def __getitem__(self, key):
        return _request_scope_context_storage.get()[key]

    def get(self, key, default=None):
        return _request_scope_context_storage.get().get(key, default)

    def exists(self) -> bool:
        try:
            _request_scope_context_storage.get()
            return True
        except LookupError:
            return False

    def copy(self):
        return self.get_data().copy()

    def get_data(self):
        return _request_scope_context_storage.get()

context = RequestContext()

# ✅ Simulate plugin injection
async def extract_context_data(request: dict) -> dict:
    return {
        "request-id": request.get("headers", {}).get("x-request-id", "missing"),
        "user-data": request.get("json", {}).get("user-id", None),
    }

# ✅ Middleware that sets context
async def context_middleware(request: dict, handler: Callable[[], Awaitable[None]]):
    token: Token = _request_scope_context_storage.set(await extract_context_data(request))
    try:
        return await handler()
    finally:
        _request_scope_context_storage.reset(token)

# ✅ Handler that reads context like blacksheep-context
async def handler():
    print("📦 request-id:", context["request-id"])
    print("👤 user-data:", context.get("user-data", "<none>"))
    print("🔍 context exists?", context.exists())

# ✅ Run simulated requests
async def main():
    print("➡️ Request A")
    await context_middleware(
        {"headers": {"x-request-id": "abc-123"}, "json": {"user-id": "alice"}},
        handler
    )

    print("\n➡️ Request B (missing user-id)")
    await context_middleware(
        {"headers": {"x-request-id": "def-456"}, "json": {}},
        handler
    )

if __name__ == "__main__":
    asyncio.run(main())
