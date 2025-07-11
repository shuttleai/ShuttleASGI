import http
import re

from libc.string cimport memcpy
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING, PyBytes_GET_SIZE
from .contents cimport Content, StreamedContent
from .cookies cimport Cookie, write_cookie_for_response
from .messages cimport Request, Response
from .url cimport URL


cdef int MAX_RESPONSE_CHUNK_SIZE = 61440  # 64kb


cdef inline bytes write_header(tuple header):
    return header[0] + b': ' + header[1] + b'\r\n'


cdef bytes write_headers(list headers):
    cdef tuple header
    cdef bytearray value

    value = bytearray()
    for header in headers:
        value.extend(write_header(header))
    return bytes(value)


cdef void extend_data_with_headers(list headers, bytearray data):
    cdef tuple header
    cdef bytes h0, h1
    
    for header in headers:
        h0 = <bytes>header[0]
        h1 = <bytes>header[1]
        data.extend(h0)
        data.extend(b': ')
        data.extend(h1)
        data.extend(b'\r\n')


cdef bytes _get_status_line(int status_code):
    try:
        return b'HTTP/1.1 ' + str(status_code).encode() + b' ' + http.HTTPStatus(status_code).phrase.encode() + b'\r\n'
    except ValueError:
        return b'HTTP/1.1 ' + str(status_code).encode() + b'\r\n'


STATUS_LINES = {
    status_code: _get_status_line(status_code) for status_code in range(100, 600)
}


cpdef bytes get_status_line(int status):
    return STATUS_LINES[status]


cdef bytes write_request_method(Request request):
    return request.method.encode()


cdef bytes write_request_uri(Request request):
    cdef bytes p
    cdef URL url = request.url
    p = url.path or b'/'
    if url.query:
        return p + b'?' + url.query
    return p


cdef void ensure_host_header(Request request):
    # TODO: if the request port is not default; add b':' + port to the Host value (?)
    if request.url.host:
        request._add_header_if_missing(b'host', request.url.host)


cdef inline bint should_use_chunked_encoding(Content content):
    return content.length < 0


cdef void set_headers_for_response_content(Response message):
    cdef Content content = message.content

    if not content:
        message._add_header(b'content-length', b'0')
        return

    message._add_header(b'content-type', content.type or b'application/octet-stream')

    if should_use_chunked_encoding(content):
        message._add_header(b'transfer-encoding', b'chunked')
    else:
        message._add_header(b'content-length', str(content.length).encode())


cdef void set_headers_for_content(Message message):
    cdef Content content = message.content

    if not content:
        message._add_header_if_missing(b'content-length', b'0')
        return

    message._add_header_if_missing(b'content-type', content.type or b'application/octet-stream')

    if should_use_chunked_encoding(content):
        message._add_header_if_missing(b'transfer-encoding', b'chunked')
    else:
        message._add_header_if_missing(b'content-length', str(content.length).encode())


cpdef bytes write_response_cookie(Cookie cookie):
    return write_cookie_for_response(cookie)


async def write_chunks(Content http_content):
    """
    Writes chunks for transfer encoding. This method only works when using
    `transfer-encoding: chunked`!
    """
    async for chunk in http_content.get_parts():
        yield (hex(len(chunk))).encode()[2:] + b'\r\n' + chunk + b'\r\n'
    yield b'0\r\n\r\n'


cdef bint is_small_response(Response response):
    cdef Content content = response.content
    if not content:
        return True
    if (
        content.length > 0
        and content.length < MAX_RESPONSE_CHUNK_SIZE
        and content.body is not None
    ):
        return True
    return False


cpdef bint is_small_request(Request request):
    cdef Content content = request.content
    if not content:
        return True
    if (
        content.length > 0
        and content.length < MAX_RESPONSE_CHUNK_SIZE
        and content.body is not None
    ):
        return True
    return False


cpdef bint request_has_body(Request request):
    cdef Content content = request.content
    if not content or content.length == 0:
        return False
    # NB: if we use chunked encoding, we don't know the content.length;
    # and it is set to -1 (in contents.pyx), therefore it is handled properly
    return True


cpdef bytes write_request_without_body(Request request):
    cdef bytearray data = bytearray()
    data.extend(write_request_method(request) + b' ' + write_request_uri(request) + b' HTTP/1.1\r\n')

    ensure_host_header(request)

    extend_data_with_headers(request._raw_headers, data)
    data.extend(b'\r\n')
    return bytes(data)


cpdef bytes write_small_request(Request request):
    cdef bytearray data = bytearray()
    data.extend(write_request_method(request) + b' ' + write_request_uri(request) + b' HTTP/1.1\r\n')

    ensure_host_header(request)
    set_headers_for_content(request)

    extend_data_with_headers(request._raw_headers, data)
    data.extend(b'\r\n')
    if request.content:
        data.extend(request.content.body)
    return bytes(data)


cdef bytes write_small_response(Response response):
    cdef bytearray data = bytearray()
    data.extend(STATUS_LINES[response.status])
    set_headers_for_content(response)
    extend_data_with_headers(response._raw_headers, data)
    data.extend(b'\r\n')
    if response.content:
        data.extend(response.content.body)
    return bytes(data)


cpdef bytes py_write_small_response(Response response):
    return write_small_response(response)


cpdef bytes py_write_small_request(Request request):
    return write_small_request(request)


async def write_request_body_only(Request request):
    # This method is used only for Expect: 100-continue scenario;
    # in such case the request headers are sent before the body
    cdef bytes data
    cdef bytes chunk
    cdef Content content

    content = request.content

    if content:
        if should_use_chunked_encoding(content):
            async for chunk in write_chunks(content):
                yield chunk
        elif isinstance(content, StreamedContent):
            async for chunk in content.get_parts():
                yield chunk
        else:
            data = content.body

            if content.length > MAX_RESPONSE_CHUNK_SIZE:
                for chunk in get_chunks(data):
                    yield chunk
            else:
                yield data
    else:
        raise ValueError('Missing request content')


async def write_request(Request request):
    cdef bytes data
    cdef bytes chunk
    cdef Content content

    ensure_host_header(request)

    set_headers_for_content(request)

    yield write_request_method(request) + b' ' + write_request_uri(request) + b' HTTP/1.1\r\n' + \
        write_headers(request._raw_headers) + b'\r\n'

    content = request.content

    if content:
        if should_use_chunked_encoding(content):
            async for chunk in write_chunks(content):
                yield chunk
        elif isinstance(content, StreamedContent):
            async for chunk in content.get_parts():
                yield chunk
        else:
            data = content.body

            if content.length > MAX_RESPONSE_CHUNK_SIZE:
                for chunk in get_chunks(data):
                    yield chunk
            else:
                yield data


def get_chunks(bytes data):
    cdef int i, data_len = len(data)
    cdef int chunk_size = MAX_RESPONSE_CHUNK_SIZE
    cdef const unsigned char[:] data_view = data
    
    for i in range(0, data_len, chunk_size):
        if i + chunk_size < data_len:
            yield bytes(data_view[i:i + chunk_size])
        else:
            yield bytes(data_view[i:])
    yield b''


async def write_response_content(Response response):
    cdef Content content
    cdef bytes data, chunk
    content = response.content

    if content:
        if should_use_chunked_encoding(content):
            async for chunk in write_chunks(content):
                yield chunk
        elif isinstance(content, StreamedContent):
            # In this case, the Content-Length is specified, but the user of
            # the library is using anyway a stream content with an async generator
            # This is particularly useful for HTTP proxies.
            async for chunk in content.get_parts():
                yield chunk
        else:
            data = content.body

            if content.length > MAX_RESPONSE_CHUNK_SIZE:
                for chunk in get_chunks(data):
                    yield chunk
            else:
                yield data


async def write_response(Response response):
    cdef bytes data
    cdef bytes chunk
    cdef Content content

    set_headers_for_content(response)

    yield STATUS_LINES[response.status] + \
        write_headers(response._raw_headers) + b'\r\n'

    async for chunk in write_response_content(response):
        yield chunk


async def send_asgi_response(Response response, object send):
    cdef bytes chunk
    cdef Content content = response.content

    set_headers_for_response_content(response)

    await send({
        'type': 'http.response.start',
        'status': response.status,
        'headers': response._raw_headers
    })

    if content:
        if content.length < 0 or isinstance(content, StreamedContent):
            # NB: ASGI HTTP Servers automatically handle chunked encoding,
            # there is no need to write the length of each chunk
            # (see write_chunks function)
            closing_chunk = False
            async for chunk in content.get_parts():
                if not chunk:
                    closing_chunk = True
                await send({
                    'type': 'http.response.body',
                    'body': chunk,
                    'more_body': bool(chunk)
                })

            if not closing_chunk:
                # This is needed, otherwise uvicorn complains with:
                # ERROR:    ASGI callable returned without completing response.
                await send({
                    'type': 'http.response.body',
                    'body': b"",
                    'more_body': False
                })
        else:
            if content.length > MAX_RESPONSE_CHUNK_SIZE:
                # Note: get_chunks yields the closing bytes fragment therefore
                # we do not need to check for the closing message!
                for chunk in get_chunks(content.body):
                    await send({
                        'type': 'http.response.body',
                        'body': chunk,
                        'more_body': bool(chunk)
                    })
            else:
                await send({
                    'type': 'http.response.body',
                    'body': content.body,
                    'more_body': False
                })
    else:
        await send({
            'type': 'http.response.body',
            'body': b''
        })


_NEW_LINES_RX = re.compile("\r\n|\n")

cdef bytes EMPTY_DATA_SSE = b"data: \n\n"


cpdef bytes write_sse(ServerSentEvent event):
    """
    Response 5: The Challenger. Minimal C-calls, no branching in hot path.
    """
    cdef:
        bytes data = event.write_data()  # Direct C-level attribute access
        Py_ssize_t data_len = len(data)
        bytes result
        char* buf
        const char* data_ptr

    if data_len == 0:
        return EMPTY_DATA_SSE

    result = PyBytes_FromStringAndSize(NULL, 6 + data_len + 2)
    if not result:
        raise MemoryError()

    buf = PyBytes_AS_STRING(result)
    data_ptr = PyBytes_AS_STRING(data)

    buf[0] = 100  # 'd'
    buf[1] = 97   # 'a'
    buf[2] = 116  # 't'
    buf[3] = 97   # 'a'
    buf[4] = 58   # ':'
    buf[5] = 32   # ' '

    memcpy(buf + 6, data_ptr, data_len)

    buf[6 + data_len] = 10  # '\n'
    buf[7 + data_len] = 10  # '\n'

    return result