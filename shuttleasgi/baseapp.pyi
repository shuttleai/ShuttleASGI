import logging
from typing import Awaitable, Callable, Dict, Optional, Type, TypeVar, Union

from shuttleasgi.exceptions import HTTPException
from shuttleasgi.messages import Request, Response
from shuttleasgi.server.application import Application
from shuttleasgi.server.routing import RouteMatch, Router

ExcT = TypeVar("ExcT", bound=Exception)

ExceptionHandlersType = Dict[
    Union[int, Type[Exception]],
    Callable[[Application, Request, ExcT], Awaitable[Response]],
]

class BaseApplication:
    router: Router
    exceptions_handlers: ExceptionHandlersType
    show_error_details: bool
    _default_404: Callable
    _default_405: Callable
    
    def __init__(self, show_error_details: bool, router: Router) -> None: ...
    def init_exceptions_handlers(self) -> ExceptionHandlersType: ...
    async def handle(self, request: Request) -> Response: ...
    async def handle_internal_server_error(
        self, request: Request, exc: Exception
    ) -> Response: ...
    async def handle_http_exception(
        self, request: Request, http_exception: HTTPException
    ) -> Response: ...
    async def handle_exception(self, request: Request, exc: Exception) -> Response: ...
    async def handle_request_handler_exception(
        self, request: Request, exc: Exception
    ) -> Response: ...
    def get_route_match(self, request: Request) -> Optional[RouteMatch]: ...
    def get_http_exception_handler(
        self, exc: HTTPException
    ) -> Optional[
        Callable[[Application, Request, HTTPException], Awaitable[Response]]
    ]: ...

def get_logger() -> logging.Logger: ...
def handle_not_found(
    app: BaseApplication, request: Request, http_exception: HTTPException
) -> Response: ...
def handle_internal_server_error(
    app: BaseApplication, request: Request, exception: Exception
) -> Response: ...