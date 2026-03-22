from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from .model import (
    CategoryRecord,
    EveDataMetadata,
    GroupRecord,
    LocalizationRecord,
    MetaGroupRecord,
    TypeRecord,
)
from .source_workspace import (
    DEFAULT_RESOURCE_BASE_URL,
    collect_category_records,
    collect_group_records,
    collect_meta_group_records,
    collect_type_records,
    load_localizations,
    resolve_icon_bytes,
    resolve_type_image,
    resolve_workspace_paths,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "src/generated/extension-ids.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "src/generated/eve"


@dataclass(frozen=True)
class ManifestRefs:
    icon_ids: set[int]
    loc_ids: set[int]
    type_ids: set[int]


@dataclass(frozen=True)
class GeneratedSummary:
    icon_count: int
    localization_count: int
    metadata: EveDataMetadata
    output_dir: Path
    type_count: int


@dataclass(frozen=True)
class GeneratedAssets:
    generated_at: str
    icon_asset_ids: set[int]
    type_image_sources: dict[int, str]


def resolve_cli_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()

    if path.is_absolute():
        return path.resolve()

    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    return (REPO_ROOT / path).resolve()


def load_manifest_refs(manifest_path: Path) -> ManifestRefs:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    eve_refs = payload.get("eveRefs", {})

    return ManifestRefs(
        icon_ids=coerce_int_set(eve_refs.get("iconIds", [])),
        loc_ids=coerce_int_set(eve_refs.get("locIds", [])),
        type_ids=coerce_int_set(eve_refs.get("typeIds", [])),
    )


def coerce_int_set(values: list[object]) -> set[int]:
    result: set[int] = set()

    for value in values:
        if not isinstance(value, int):
            raise TypeError(f"Expected integer ID in manifest, got {value!r}")
        result.add(value)

    return result


def generate_docs_data(
    *,
    workspace_arg: str | None,
    resfileindex_arg: str | None,
    fsd_dir_arg: str | None,
    start_ini_arg: str | None,
    resource_cache_dir_arg: str | None,
    resource_base_url: str = DEFAULT_RESOURCE_BASE_URL,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> GeneratedSummary:
    refs = load_manifest_refs(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    workspace = resolve_workspace_paths(
        workspace_arg=workspace_arg,
        resfileindex_arg=resfileindex_arg,
        fsd_dir_arg=fsd_dir_arg,
        start_ini_arg=start_ini_arg,
        resource_cache_dir_arg=resource_cache_dir_arg,
        resource_base_url=resource_base_url,
        resolve_cli_path=resolve_cli_path,
    )
    fsd = workspace["fsd"]
    metadata = workspace["metadata"]
    resource_index = workspace["resource_index"]

    if metadata.server_id != "tq":
        raise ValueError(
            f"Only Tranquility data is supported right now, got: {metadata.server_id}"
        )

    type_records = collect_type_records(fsd, refs.type_ids)
    group_records = collect_group_records(
        fsd,
        {record.group_id for record in type_records.values()},
    )
    category_records = collect_category_records(
        fsd,
        {record.category_id for record in group_records.values()},
    )
    meta_group_records = collect_meta_group_records(
        fsd,
        {
            record.meta_group_id
            for record in type_records.values()
            if record.meta_group_id is not None
        },
    )
    localizations = load_localizations(
        resource_index,
        collect_needed_localization_ids(
            refs=refs,
            type_records=type_records,
            group_records=group_records,
            category_records=category_records,
            meta_group_records=meta_group_records,
        ),
    )
    generated_assets = write_generated_assets(
        fsd=fsd,
        resource_index=resource_index,
        output_dir=output_dir,
        refs=refs,
        type_records=type_records,
        group_records=group_records,
        meta_group_records=meta_group_records,
    )
    write_generated_data_file(
        metadata=metadata,
        generated_assets=generated_assets,
        localizations=localizations,
        output_dir=output_dir,
        type_records=type_records,
        group_records=group_records,
        category_records=category_records,
        meta_group_records=meta_group_records,
    )

    return GeneratedSummary(
        icon_count=len(generated_assets.icon_asset_ids),
        localization_count=len(localizations),
        metadata=metadata,
        output_dir=output_dir,
        type_count=len(type_records),
    )


def collect_needed_localization_ids(
    *,
    refs: ManifestRefs,
    type_records: dict[int, TypeRecord],
    group_records: dict[int, GroupRecord],
    category_records: dict[int, CategoryRecord],
    meta_group_records: dict[int, MetaGroupRecord],
) -> set[int]:
    needed_loc_ids = set(refs.loc_ids)

    for type_record in type_records.values():
        needed_loc_ids.add(type_record.type_name_id)

        if type_record.description_id is not None:
            needed_loc_ids.add(type_record.description_id)

        group_record = group_records.get(type_record.group_id)
        if group_record is not None:
            needed_loc_ids.add(group_record.group_name_id)

            category_record = category_records.get(group_record.category_id)
            if category_record is not None:
                needed_loc_ids.add(category_record.category_name_id)

        if type_record.meta_group_id is not None:
            meta_group_record = meta_group_records.get(type_record.meta_group_id)
            if meta_group_record is not None:
                needed_loc_ids.add(meta_group_record.name_id)

    return needed_loc_ids


def write_generated_assets(
    *,
    fsd,
    resource_index,
    output_dir: Path,
    refs: ManifestRefs,
    type_records: dict[int, TypeRecord],
    group_records: dict[int, GroupRecord],
    meta_group_records: dict[int, MetaGroupRecord],
) -> GeneratedAssets:
    icon_output_dir = output_dir / "icons"
    type_output_dir = output_dir / "types"
    reset_generated_directory(icon_output_dir)
    reset_generated_directory(type_output_dir)

    icon_asset_ids = set(refs.icon_ids)
    for type_record in type_records.values():
        if type_record.meta_group_id is None:
            continue

        meta_group_record = meta_group_records.get(type_record.meta_group_id)
        if meta_group_record is not None and meta_group_record.icon_id is not None:
            icon_asset_ids.add(meta_group_record.icon_id)

    resolved_icon_asset_ids: set[int] = set()
    for icon_id in sorted(icon_asset_ids):
        try:
            icon_bytes = resolve_icon_bytes(
                fsd=fsd,
                resource_index=resource_index,
                icon_id=icon_id,
            )
        except FileNotFoundError:
            continue

        if icon_bytes is None:
            continue

        (icon_output_dir / f"{icon_id}.png").write_bytes(icon_bytes)
        resolved_icon_asset_ids.add(icon_id)

    type_image_sources: dict[int, str] = {}
    for type_id, type_record in sorted(type_records.items()):
        category_id = None
        group_record = group_records.get(type_record.group_id)
        if group_record is not None:
            category_id = group_record.category_id

        try:
            resolved_image = resolve_type_image(
                fsd=fsd,
                resource_index=resource_index,
                type_record=type_record,
                category_id=category_id,
            )
        except FileNotFoundError:
            continue

        if resolved_image is None:
            continue

        (type_output_dir / f"{type_id}.png").write_bytes(resolved_image.bytes_)
        type_image_sources[type_id] = resolved_image.source

    return GeneratedAssets(
        generated_at=datetime.now(timezone.utc).isoformat(),
        icon_asset_ids=resolved_icon_asset_ids,
        type_image_sources=type_image_sources,
    )


def reset_generated_directory(target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)


def write_generated_data_file(
    *,
    metadata: EveDataMetadata,
    generated_assets: GeneratedAssets,
    localizations: dict[int, LocalizationRecord],
    output_dir: Path,
    type_records: dict[int, TypeRecord],
    group_records: dict[int, GroupRecord],
    category_records: dict[int, CategoryRecord],
    meta_group_records: dict[int, MetaGroupRecord],
) -> None:
    data_file = output_dir / "data.ts"
    data_file.write_text(
        render_data_module(
            metadata=metadata,
            generated_assets=generated_assets,
            localizations=localizations,
            output_dir=output_dir,
            type_records=type_records,
            group_records=group_records,
            category_records=category_records,
            meta_group_records=meta_group_records,
        ),
        encoding="utf-8",
    )


def render_data_module(
    *,
    metadata: EveDataMetadata,
    generated_assets: GeneratedAssets,
    localizations: dict[int, LocalizationRecord],
    output_dir: Path,
    type_records: dict[int, TypeRecord],
    group_records: dict[int, GroupRecord],
    category_records: dict[int, CategoryRecord],
    meta_group_records: dict[int, MetaGroupRecord],
) -> str:
    lines = [
        "import type {",
        "    EveDataMetadata,",
        "    EveIconEntry,",
        "    EveLocalizationEntry,",
        "    EveTypeEntry,",
        '} from "./schema";',
    ]

    icon_assets = [
        icon_id
        for icon_id in sorted(generated_assets.icon_asset_ids)
        if (output_dir / "icons" / f"{icon_id}.png").exists()
    ]
    type_assets = [
        type_id
        for type_id in sorted(type_records)
        if (output_dir / "types" / f"{type_id}.png").exists()
    ]

    for icon_id in icon_assets:
        lines.append(f'import icon{icon_id}Url from "./icons/{icon_id}.png?url";')

    for type_id in type_assets:
        lines.append(f'import type{type_id}Url from "./types/{type_id}.png?url";')

    lines.extend(
        [
            "",
            f"export const eveGeneratedAt = {render_string(generated_assets.generated_at)};",
            "",
            "export const eveDataMetadata: EveDataMetadata | null = {",
            f"    serverId: {render_string(metadata.server_id)},",
            "    serverName: {",
            f"        en: {render_string(metadata.server_name_en)},",
            f"        zhCN: {render_string(metadata.server_name_zh)},",
            "    },",
        ]
    )

    if metadata.game_build is not None or metadata.game_version is not None:
        lines.extend(
            [
                "    game: {",
                f"        build: {render_optional_string(metadata.game_build)},",
                f"        version: {render_optional_string(metadata.game_version)},",
                "    },",
            ]
        )

    lines.extend(
        [
            "};",
            "",
            "export const eveLocalizations: Record<number, EveLocalizationEntry> = {",
        ]
    )

    for loc_id, record in sorted(localizations.items()):
        lines.append(
            f"    {loc_id}: {{ en: {render_string(record.en)}, zhCN: {render_string(record.zh_cn)} }},"
        )

    lines.extend(
        [
            "};",
            "",
            "export const eveIcons: Record<number, EveIconEntry> = {",
        ]
    )

    for icon_id in icon_assets:
        lines.append(f"    {icon_id}: {{ iconId: {icon_id}, src: icon{icon_id}Url }},")

    lines.extend(
        [
            "};",
            "",
            "export const eveTypes: Record<number, EveTypeEntry> = {",
        ]
    )

    for type_id, record in sorted(type_records.items()):
        type_lines = [
            f"    {type_id}: {{",
            f"        groupId: {record.group_id},",
        ]

        group_record = group_records.get(record.group_id)
        if group_record is not None:
            type_lines.append(f"        groupNameLocId: {group_record.group_name_id},")
            type_lines.append(f"        categoryId: {group_record.category_id},")

            category_record = category_records.get(group_record.category_id)
            if category_record is not None:
                type_lines.append(
                    f"        categoryNameLocId: {category_record.category_name_id},"
                )

        if record.description_id is not None:
            type_lines.append(f"        descriptionLocId: {record.description_id},")

        if record.graphic_id is not None:
            type_lines.append(f"        graphicId: {record.graphic_id},")

        if record.icon_id is not None:
            type_lines.append(f"        iconId: {record.icon_id},")

        if record.meta_group_id is not None:
            type_lines.append(f"        metaGroupId: {record.meta_group_id},")
            meta_group_record = meta_group_records.get(record.meta_group_id)
            if meta_group_record is not None:
                type_lines.append(
                    f"        metaGroupNameLocId: {meta_group_record.name_id},"
                )
                if meta_group_record.icon_id is not None:
                    type_lines.append(
                        f"        metaGroupIconId: {meta_group_record.icon_id},"
                    )

        if type_id in type_assets:
            type_lines.append(
                f"        imageSource: {render_string(generated_assets.type_image_sources[type_id])},"
            )
            type_lines.append(f"        imageSrc: type{type_id}Url,")

        type_lines.extend(
            [
                f"        typeId: {type_id},",
                f"        typeNameLocId: {record.type_name_id},",
                "    },",
            ]
        )

        lines.extend(type_lines)

    lines.extend(
        [
            "};",
            "",
        ]
    )

    return "\n".join(lines)


def render_optional_string(value: str | None) -> str:
    return "null" if value is None else render_string(value)


def render_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)
