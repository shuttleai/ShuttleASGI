
cdef class InvalidOperation(Exception):

    def __init__(self, str message, object inner_exception=None):
        super().__init__(message)
        self.inner_exception = inner_exception


cdef class HTTPException(Exception):

    def __init__(self, int status, str message = "HTTP exception"):
        super().__init__(message)
        self.status = status


cdef class BadRequest(HTTPException):

    def __init__(self, message=None):
        super().__init__(400, message or "Bad request")


cdef class BadRequestFormat(BadRequest):

    def __init__(self, str message, object inner_exception=None):
        super().__init__(message)
        self.inner_exception = inner_exception


cdef class FailedRequestError(HTTPException):
    def __init__(self, int status, str data) -> None:
        super().__init__(
            status, f"The response status code does not indicate success: {status}. Response body: {data}"
        )
        self.data = data


cdef class WrongMethod(HTTPException):

    def __init__(self, message=None):
        super().__init__(405, message or "Wrong method")


cdef class NotFound(HTTPException):

    def __init__(self, message=None):
        super().__init__(404, message or "Not found")


cdef class Unauthorized(HTTPException):

    def __init__(self, message=None):
        super().__init__(401, message or "Unauthorized")


cdef class Forbidden(HTTPException):

    def __init__(self, message=None):
        super().__init__(403, message or "Forbidden")


cdef class Conflict(HTTPException):

    def __init__(self, message=None):
        super().__init__(409, message or "Conflict")


cdef class RangeNotSatisfiable(HTTPException):

    def __init__(self):
        super().__init__(416, "Range not satisfiable")


cdef class InternalServerError(HTTPException):

    def __init__(self, Exception source_error = None):
        super().__init__(500, "Internal server error")
        self.source_error = source_error


cdef class NotImplementedByServer(HTTPException):

    def __init__(self):
        super().__init__(501, "Not implemented by server")


cdef class ServiceUnavailable(HTTPException):

    def __init__(self):
        super().__init__(503, "Service unavailable")


cdef class InvalidArgument(Exception):

    def __init__(self, str message):
        super().__init__(message)


cdef class MessageAborted(Exception):
    def __init__(self):
        super().__init__(
            "The message was aborted before the client sent its whole content."
        )
