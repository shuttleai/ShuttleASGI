from shuttleasgi.messages import Request

import uuid_utils as uuid


class RequestIDMiddleware:
    def __init__(self, header_name: bytes = b"X-Request-ID") -> None:
        self.header_name = header_name
        self.prefix = b"req_"

    async def __call__(self, request: Request, handler):
        value: bytes = self.prefix + uuid.uuid4().hex.encode("utf-8")
        request.sai["raw_req_id"] = value

        response = await handler(request)

        response.add_header(self.header_name, value)

        return response
