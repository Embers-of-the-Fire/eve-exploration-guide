from __future__ import annotations

from typing import Any

import msgpack


def loads(payload: bytes) -> Any:
    return msgpack.unpackb(payload, raw=False, strict_map_key=False)
