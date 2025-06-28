import timeit
import orjson as json
import secrets

_JSON_OPTIONS = json.OPT_SERIALIZE_NUMPY | json.OPT_SERIALIZE_UUID

def decode_no_args(obj) -> str:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    ).decode()

def decode_with_utf8(obj) -> str:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    ).decode("utf-8")

def decode_with_ascii(obj) -> str:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    ).decode("ascii")

def decode_with_bytes(obj) -> bytes:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    )

def decode_no_args_precomputed_options(obj) -> str:
    return json.dumps(
        obj,
        option=_JSON_OPTIONS
    ).decode()

test_obj = {
    "key1": "value1",
    "key2": 123,
    "key3": [1, 2, 3],
    "key4": {"nested_key": "nested_value"},
}

# warm up
for _ in range(1000):
    decode_no_args(test_obj)
    decode_with_utf8(test_obj)
    decode_with_ascii(test_obj)
    decode_with_bytes(test_obj)
    decode_no_args_precomputed_options(test_obj)

print("decode_no_args:", timeit.timeit(lambda: decode_no_args(test_obj), number=100_000))
print("decode_with_utf8:", timeit.timeit(lambda: decode_with_utf8(test_obj), number=100_000))
print("decode_with_ascii:", timeit.timeit(lambda: decode_with_ascii(test_obj), number=100_000))
print("decode_with_bytes:", timeit.timeit(lambda: decode_with_bytes(test_obj), number=100_000))
print("decode_no_args_precomputed_options:", timeit.timeit(lambda: decode_no_args_precomputed_options(test_obj), number=100_000))
