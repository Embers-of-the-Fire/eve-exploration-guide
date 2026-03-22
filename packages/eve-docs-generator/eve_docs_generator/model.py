from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BLUEPRINT_CATEGORY_ID = 9
TQ_SERVER_ID = "tq"
TQ_SERVER_NAME_EN = "Tranquility"
TQ_SERVER_NAME_ZH = "宁静"

TypeImageSource = Literal["graphic", "graphic-blueprint", "icon"]


@dataclass(frozen=True)
class EveDataMetadata:
    game_build: str | None
    game_version: str | None
    server_id: str = TQ_SERVER_ID
    server_name_en: str = TQ_SERVER_NAME_EN
    server_name_zh: str = TQ_SERVER_NAME_ZH


@dataclass(frozen=True)
class LocalizationRecord:
    en: str
    zh_cn: str


@dataclass(frozen=True)
class TypeRecord:
    description_id: int | None
    graphic_id: int | None
    group_id: int
    icon_id: int | None
    meta_group_id: int | None
    published: bool
    type_id: int
    type_name_id: int


@dataclass(frozen=True)
class GroupRecord:
    category_id: int
    group_id: int
    group_name_id: int
    published: bool


@dataclass(frozen=True)
class CategoryRecord:
    category_id: int
    category_name_id: int
    published: bool


@dataclass(frozen=True)
class MetaGroupRecord:
    icon_id: int | None
    meta_group_id: int
    name_id: int


@dataclass(frozen=True)
class ResourceEntry:
    checksum: str | None
    file_name: str
    resource_path: str
    url: str


@dataclass(frozen=True)
class ResolvedTypeImage:
    bytes_: bytes
    source: TypeImageSource
