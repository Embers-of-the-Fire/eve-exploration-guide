from __future__ import annotations

import struct


class MsgpackDecoder:
    def __init__(self, payload: bytes):
        self._payload = payload
        self._offset = 0

    def unpack(self):
        value = self._unpack()

        if self._offset != len(self._payload):
            raise ValueError("Extra trailing bytes found after MessagePack payload")

        return value

    def _read(self, length: int) -> bytes:
        end = self._offset + length

        if end > len(self._payload):
            raise ValueError("Unexpected end of MessagePack payload")

        chunk = self._payload[self._offset : end]
        self._offset = end
        return chunk

    def _read_struct(self, format_string: str):
        size = struct.calcsize(format_string)
        return struct.unpack(format_string, self._read(size))[0]

    def _unpack_map(self, size: int):
        result = {}

        for _ in range(size):
            key = self._unpack()
            value = self._unpack()
            result[key] = value

        return result

    def _unpack_array(self, size: int):
        return [self._unpack() for _ in range(size)]

    def _unpack(self):
        prefix = self._read(1)[0]

        if prefix <= 0x7F:
            return prefix

        if prefix >= 0xE0:
            return prefix - 0x100

        if 0x80 <= prefix <= 0x8F:
            return self._unpack_map(prefix & 0x0F)

        if 0x90 <= prefix <= 0x9F:
            return self._unpack_array(prefix & 0x0F)

        if 0xA0 <= prefix <= 0xBF:
            return self._read(prefix & 0x1F).decode("utf-8")

        if prefix == 0xC0:
            return None

        if prefix == 0xC2:
            return False

        if prefix == 0xC3:
            return True

        if prefix == 0xC4:
            return self._read(self._read_struct(">B"))

        if prefix == 0xC5:
            return self._read(self._read_struct(">H"))

        if prefix == 0xC6:
            return self._read(self._read_struct(">I"))

        if prefix in {0xC7, 0xC8, 0xC9, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8}:
            raise ValueError(
                f"Unsupported MessagePack extension type prefix: 0x{prefix:02x}"
            )

        if prefix == 0xCA:
            return self._read_struct(">f")

        if prefix == 0xCB:
            return self._read_struct(">d")

        if prefix == 0xCC:
            return self._read_struct(">B")

        if prefix == 0xCD:
            return self._read_struct(">H")

        if prefix == 0xCE:
            return self._read_struct(">I")

        if prefix == 0xCF:
            return self._read_struct(">Q")

        if prefix == 0xD0:
            return self._read_struct(">b")

        if prefix == 0xD1:
            return self._read_struct(">h")

        if prefix == 0xD2:
            return self._read_struct(">i")

        if prefix == 0xD3:
            return self._read_struct(">q")

        if prefix == 0xD9:
            return self._read(self._read_struct(">B")).decode("utf-8")

        if prefix == 0xDA:
            return self._read(self._read_struct(">H")).decode("utf-8")

        if prefix == 0xDB:
            return self._read(self._read_struct(">I")).decode("utf-8")

        if prefix == 0xDC:
            return self._unpack_array(self._read_struct(">H"))

        if prefix == 0xDD:
            return self._unpack_array(self._read_struct(">I"))

        if prefix == 0xDE:
            return self._unpack_map(self._read_struct(">H"))

        if prefix == 0xDF:
            return self._unpack_map(self._read_struct(">I"))

        raise ValueError(f"Unsupported MessagePack prefix: 0x{prefix:02x}")


def loads(payload: bytes):
    return MsgpackDecoder(payload).unpack()
