import {
    eveFitSectionOrder,
    type EveFitSectionKey,
} from "../../../src/components/docs/eve/EveFit.sections";

export type ExtensionIdKind = "text" | "icon" | "image";
export type EveRefKind = "icon" | "localization" | "type";

export interface ExtensionIdEntry {
    component: string;
    file: string;
    id: string;
    kind: ExtensionIdKind;
    line: number;
}

export interface ExtensionIdUnresolved {
    component: string;
    expectedProp: string;
    file: string;
    line: number;
}

export interface EveRefEntry {
    component: string;
    file: string;
    id: number;
    kind: EveRefKind;
    line: number;
    prop: string;
}

export interface EveRefUnresolved {
    component: string;
    expectedProp: string;
    file: string;
    kind: EveRefKind;
    line: number;
}

export interface ExtensionIdManifest {
    duplicates: Array<{
        id: string;
        occurrences: Array<{
            component: string;
            file: string;
            kind: ExtensionIdKind;
            line: number;
        }>;
    }>;
    entries: ExtensionIdEntry[];
    eveRefs: {
        duplicates: Array<{
            id: number;
            kind: EveRefKind;
            occurrences: Array<{
                component: string;
                file: string;
                line: number;
                prop: string;
            }>;
        }>;
        entries: EveRefEntry[];
        iconIds: number[];
        locIds: number[];
        typeIds: number[];
        unresolved: EveRefUnresolved[];
    };
    generatedAt: string;
    unresolved: ExtensionIdUnresolved[];
}

export interface ExtensionIdRenderMeta {
    file: string;
    line: number;
}

export interface WithExtensionIdSourceProps {
    __extensionIdFile?: string;
    __extensionIdLine?: number | string;
}

interface ExtensionIdCollectorState {
    enabled: boolean;
    entries: Map<string, ExtensionIdEntry>;
    eveEntries: Map<string, EveRefEntry>;
    eveUnresolved: Map<string, EveRefUnresolved>;
    unresolved: Map<string, ExtensionIdUnresolved>;
}

const collectorStateKey = "__eveExtensionIdCollectorState__";

function createCollectorState(): ExtensionIdCollectorState {
    return {
        enabled: false,
        entries: new Map(),
        eveEntries: new Map(),
        eveUnresolved: new Map(),
        unresolved: new Map(),
    };
}

function getCollectorState(): ExtensionIdCollectorState {
    const globalState = globalThis as typeof globalThis & {
        [collectorStateKey]?: ExtensionIdCollectorState;
    };

    globalState[collectorStateKey] ??= createCollectorState();
    return globalState[collectorStateKey];
}

function toMapKey(values: Array<number | string>) {
    return values.join("\u0000");
}

function compareEntries(left: ExtensionIdEntry, right: ExtensionIdEntry) {
    return (
        left.id.localeCompare(right.id) ||
        left.file.localeCompare(right.file) ||
        left.line - right.line
    );
}

function compareEveEntries(left: EveRefEntry, right: EveRefEntry) {
    return (
        left.kind.localeCompare(right.kind) ||
        left.id - right.id ||
        left.file.localeCompare(right.file) ||
        left.line - right.line ||
        left.prop.localeCompare(right.prop)
    );
}

function compareUnresolved(
    left: ExtensionIdUnresolved,
    right: ExtensionIdUnresolved,
) {
    return (
        left.file.localeCompare(right.file) ||
        left.line - right.line ||
        left.component.localeCompare(right.component) ||
        left.expectedProp.localeCompare(right.expectedProp)
    );
}

function compareEveUnresolved(left: EveRefUnresolved, right: EveRefUnresolved) {
    return (
        left.file.localeCompare(right.file) ||
        left.line - right.line ||
        left.component.localeCompare(right.component) ||
        left.kind.localeCompare(right.kind) ||
        left.expectedProp.localeCompare(right.expectedProp)
    );
}

function collectDuplicates(entries: ExtensionIdEntry[]) {
    const byId = new Map<
        string,
        ExtensionIdManifest["duplicates"][number]["occurrences"]
    >();

    for (const entry of entries) {
        const bucket = byId.get(entry.id) ?? [];
        bucket.push({
            component: entry.component,
            file: entry.file,
            kind: entry.kind,
            line: entry.line,
        });
        byId.set(entry.id, bucket);
    }

    return [...byId.entries()]
        .filter(([, occurrences]) => occurrences.length > 1)
        .map(([id, occurrences]) => ({
            id,
            occurrences,
        }))
        .sort((left, right) => left.id.localeCompare(right.id));
}

function collectEveDuplicates(entries: EveRefEntry[]) {
    const byRef = new Map<
        string,
        ExtensionIdManifest["eveRefs"]["duplicates"][number]
    >();

    for (const entry of entries) {
        const key = `${entry.kind}:${entry.id}`;
        const bucket = byRef.get(key) ?? {
            id: entry.id,
            kind: entry.kind,
            occurrences: [],
        };

        bucket.occurrences.push({
            component: entry.component,
            file: entry.file,
            line: entry.line,
            prop: entry.prop,
        });
        byRef.set(key, bucket);
    }

    return [...byRef.values()]
        .filter((entry) => entry.occurrences.length > 1)
        .sort(
            (left, right) =>
                left.kind.localeCompare(right.kind) || left.id - right.id,
        );
}

function collectEveIdList(entries: EveRefEntry[], kind: EveRefKind) {
    return [
        ...new Set(
            entries
                .filter((entry) => entry.kind === kind)
                .map((entry) => entry.id),
        ),
    ].sort((left, right) => left - right);
}

function isRenderableStringId(value: unknown): value is string {
    return typeof value === "string" && value.trim().length > 0;
}

function isSafeIntegerId(value: unknown): value is number {
    return typeof value === "number" && Number.isSafeInteger(value);
}

function isCollectionActive(
    meta: ExtensionIdRenderMeta | undefined,
): meta is ExtensionIdRenderMeta {
    return getCollectorState().enabled && meta !== undefined;
}

function recordExtensionEntry(
    component: string,
    kind: ExtensionIdKind,
    id: string,
    meta: ExtensionIdRenderMeta,
) {
    const state = getCollectorState();
    const key = toMapKey([component, kind, id, meta.file, meta.line]);

    state.entries.set(key, {
        component,
        file: meta.file,
        id,
        kind,
        line: meta.line,
    });
}

function recordExtensionUnresolved(
    component: string,
    expectedProp: string,
    meta: ExtensionIdRenderMeta,
) {
    const state = getCollectorState();
    const key = toMapKey([component, expectedProp, meta.file, meta.line]);

    state.unresolved.set(key, {
        component,
        expectedProp,
        file: meta.file,
        line: meta.line,
    });
}

function recordEveEntry(
    component: string,
    kind: EveRefKind,
    prop: string,
    id: number,
    meta: ExtensionIdRenderMeta,
) {
    const state = getCollectorState();
    const key = toMapKey([component, kind, prop, id, meta.file, meta.line]);

    state.eveEntries.set(key, {
        component,
        file: meta.file,
        id,
        kind,
        line: meta.line,
        prop,
    });
}

function recordEveUnresolved(
    component: string,
    kind: EveRefKind,
    expectedProp: string,
    meta: ExtensionIdRenderMeta,
) {
    const state = getCollectorState();
    const key = toMapKey([component, kind, expectedProp, meta.file, meta.line]);

    state.eveUnresolved.set(key, {
        component,
        expectedProp,
        file: meta.file,
        kind,
        line: meta.line,
    });
}

function registerStringReference(
    component: string,
    kind: ExtensionIdKind,
    expectedProp: string,
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    if (!isCollectionActive(meta)) {
        return;
    }

    if (!isRenderableStringId(value)) {
        recordExtensionUnresolved(component, expectedProp, meta);
        return;
    }

    recordExtensionEntry(component, kind, value, meta);
}

function registerEveReference(
    component: string,
    kind: EveRefKind,
    expectedProp: string,
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    if (!isCollectionActive(meta)) {
        return;
    }

    if (!isSafeIntegerId(value)) {
        recordEveUnresolved(component, kind, expectedProp, meta);
        return;
    }

    recordEveEntry(component, kind, expectedProp, value, meta);
}

function registerEveFitSection(
    component: string,
    section: EveFitSectionKey,
    value: unknown,
    meta: ExtensionIdRenderMeta,
) {
    const expectedProp = `data.${section}[].id`;

    if (value === undefined) {
        return;
    }

    if (!Array.isArray(value)) {
        recordEveUnresolved(component, "type", expectedProp, meta);
        return;
    }

    const sectionIds: number[] = [];

    for (const entry of value) {
        if (
            typeof entry !== "object" ||
            entry === null ||
            Array.isArray(entry) ||
            !("id" in entry) ||
            !isSafeIntegerId(entry.id)
        ) {
            recordEveUnresolved(component, "type", expectedProp, meta);
            return;
        }

        sectionIds.push(entry.id);
    }

    for (const id of sectionIds) {
        recordEveEntry(component, "type", expectedProp, id, meta);
    }
}

export function resolveExtensionIdRenderMeta(
    file: string | undefined,
    line: number | string | undefined,
): ExtensionIdRenderMeta | undefined {
    if (typeof file !== "string" || file.length === 0) {
        return undefined;
    }

    const parsedLine =
        typeof line === "number" ? line : line ? Number.parseInt(line, 10) : 1;

    return {
        file,
        line:
            Number.isSafeInteger(parsedLine) && parsedLine > 0 ? parsedLine : 1,
    };
}

export function clearExtensionIdCollection() {
    const state = getCollectorState();

    state.entries.clear();
    state.eveEntries.clear();
    state.eveUnresolved.clear();
    state.unresolved.clear();
}

export function setExtensionIdCollectionEnabled(enabled: boolean) {
    getCollectorState().enabled = enabled;
}

export function buildExtensionIdManifest(): ExtensionIdManifest {
    const state = getCollectorState();
    const entries = [...state.entries.values()].sort(compareEntries);
    const unresolved = [...state.unresolved.values()].sort(compareUnresolved);
    const eveEntries = [...state.eveEntries.values()].sort(compareEveEntries);
    const eveUnresolved = [...state.eveUnresolved.values()].sort(
        compareEveUnresolved,
    );

    return {
        duplicates: collectDuplicates(entries),
        entries,
        eveRefs: {
            duplicates: collectEveDuplicates(eveEntries),
            entries: eveEntries,
            iconIds: collectEveIdList(eveEntries, "icon"),
            locIds: collectEveIdList(eveEntries, "localization"),
            typeIds: collectEveIdList(eveEntries, "type"),
            unresolved: eveUnresolved,
        },
        generatedAt: new Date().toISOString(),
        unresolved,
    };
}

export function registerTextExtensionId(
    component: string,
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerStringReference(component, "text", "id", value, meta);
}

export function registerIconExtensionId(
    component: string,
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerStringReference(component, "icon", "id", value, meta);
}

export function registerImageExtensionId(
    component: string,
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerStringReference(component, "image", "id", value, meta);
}

export function registerLocalizedIconTextExtensionIds(
    id: unknown,
    iconId: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerStringReference("LocalizedIconText", "text", "id", id, meta);
    registerStringReference(
        "LocalizedIconText",
        "icon",
        "iconId",
        iconId,
        meta,
    );
}

export function registerEveTypeId(
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerEveReference("EveType", "type", "typeId", value, meta);
}

export function registerEveLocId(
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerEveReference("EveLocText", "localization", "locId", value, meta);
}

export function registerEveIconId(
    value: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    registerEveReference("EveIcon", "icon", "iconId", value, meta);
}

export function registerEveFitRefs(
    shipId: unknown,
    data: unknown,
    meta: ExtensionIdRenderMeta | undefined,
) {
    if (!isCollectionActive(meta)) {
        return;
    }

    registerEveReference("EveFit", "type", "shipId", shipId, meta);

    if (typeof data !== "object" || data === null || Array.isArray(data)) {
        for (const section of eveFitSectionOrder) {
            recordEveUnresolved("EveFit", "type", `data.${section}[].id`, meta);
        }
        return;
    }

    const fitData = data as Record<string, unknown>;

    for (const section of eveFitSectionOrder) {
        registerEveFitSection("EveFit", section, fitData[section], meta);
    }
}
