import orjson as json

from typing import Any

from essentials.json import dumps


def default_json_dumps(obj) -> str:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    ).decode("utf-8")


def default_pretty_json_dumps(obj) -> str:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
            | json.OPT_INDENT_2
        )
    ).decode("utf-8")


def orjson_dumps(obj) -> bytes:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    )


def orjson_pretty_dumps(obj) -> bytes:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
            | json.OPT_INDENT_2
        )
    )


def builtin_json_dumps(obj) -> str:
    return dumps(obj, separators=(",", ":"))


def builtin_pretty_json_dumps(obj) -> str:
    return dumps(obj, indent=4)


class JSONSettings:
    def __init__(self):
        self._loads = json.loads
        self._dumps = default_json_dumps
        self._pretty_dumps = default_pretty_json_dumps
        self._odumps = orjson_dumps
        self._opretty_dumps = orjson_pretty_dumps

    def use(
        self,
        loads=json.loads,
        dumps=default_json_dumps,
        pretty_dumps=default_pretty_json_dumps,
    ):
        self._loads = loads
        self._dumps = dumps
        self._pretty_dumps = pretty_dumps
        self._odumps = orjson_dumps
        self._opretty_dumps = orjson_pretty_dumps

    def loads(self, text: str) -> Any:
        return self._loads(text)

    def dumps(self, obj: Any) -> str:
        return self._dumps(obj)

    def pretty_dumps(self, obj: Any) -> str:
        return self._pretty_dumps(obj)

    def odumps(self, obj: Any) -> bytes:
        return self._odumps(obj)

    def opretty_dumps(self, obj: Any) -> bytes:
        return self._opretty_dumps(obj)


json_settings = JSONSettings()
