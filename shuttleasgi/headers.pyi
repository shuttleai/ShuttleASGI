from collections.abc import Iterator
from typing import Dict, List, Tuple, Union, overload, Optional

class Header:
    name: bytes
    value: bytes
    def __init__(self, name: bytes, value: bytes) -> None: ...
    def __iter__(self) -> Iterator[bytes]: ...

HeaderType = Tuple[bytes, bytes]

class Headers:
    def __init__(self, values: Optional[List[HeaderType]] = None):
        self.values = values

    def get(self, name: bytes) -> tuple[bytes, ...]: ...
    def get_tuples(self, name: bytes) -> list[tuple[bytes, bytes]]: ...
    def get_first(self, key: bytes) -> bytes | None: ...
    def get_single(self, key: bytes) -> bytes: ...
    def merge(self, values: list[tuple[bytes, bytes]]) -> None: ...
    def update(self, values: dict[bytes, bytes]) -> None: ...
    def items(self) -> Iterator[tuple[bytes, bytes]]: ...
    def clone(self) -> "Headers": ...
    def add_many(self, values: Union[Dict[bytes, bytes], List[Tuple[bytes, bytes]]]) -> None: ...

    def __add__(self, other) -> "Headers": ...
    def __radd__(self, other) -> "Headers": ...
    def __iadd__(self, other) -> "Headers": ...

    def __iter__(self) -> Iterator[tuple[bytes, bytes]]: ...
    
    def __getitem__(self, item: bytes) -> tuple[bytes, ...]: ...
    def __setitem__(self, key: bytes, value: bytes) -> None: ...
    def __delitem__(self, key: bytes) -> None: ...
    def __contains__(self, key: bytes) -> bool: ...
    def __len__(self) -> int: ...

    def keys(self) -> tuple[bytes, ...]: ...
    def add(self, name: bytes, value: bytes) -> None: ...
    def set(self, name: bytes, value: bytes) -> None: ...
    def remove(self, key: bytes) -> None: ...
    def contains(self, key: bytes) -> bool: ...