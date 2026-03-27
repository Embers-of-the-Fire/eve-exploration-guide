import { getTypeEntry, resolveLocalization } from "./data";

export interface EveFitEntry {
    count?: number;
    id: number;
}

export const eveFitSectionOrder = [
    "high",
    "med",
    "low",
    "rig",
    "charges",
    "drones",
    "cargo",
] as const;

export type EveFitSectionKey = (typeof eveFitSectionOrder)[number];

export interface EveFitData {
    cargo?: EveFitEntry[];
    charges?: EveFitEntry[];
    drones?: EveFitEntry[];
    high?: EveFitEntry[];
    low?: EveFitEntry[];
    med?: EveFitEntry[];
    rig?: EveFitEntry[];
}

export interface ResolvedFitEntry {
    categoryId?: number;
    count: number;
    id: number;
    name: ReturnType<typeof resolveTypeName>;
}

export interface ResolvedFitSection {
    entries: ResolvedFitEntry[];
    key: EveFitSectionKey;
}

export interface RenderedFitRow {
    countLabel: string | null;
    id: number;
    key: string;
}

function normalizeCount(value: number | undefined): number {
    return typeof value === "number" && Number.isSafeInteger(value) && value > 0
        ? value
        : 1;
}

export function resolveTypeName(typeId: number) {
    const typeData = getTypeEntry(typeId);

    return resolveLocalization(typeData?.typeNameLocId, "type", typeId);
}

export function shouldExpandCount(categoryId: number | undefined) {
    return categoryId === 7;
}

export function resolveFitEntries(entries: EveFitEntry[]): ResolvedFitEntry[] {
    return entries.map((entry) => {
        const typeData = getTypeEntry(entry.id);

        return {
            categoryId: typeData?.categoryId,
            count: normalizeCount(entry.count),
            id: entry.id,
            name: resolveTypeName(entry.id),
        };
    });
}

export function resolveFitSections(data: EveFitData): ResolvedFitSection[] {
    return eveFitSectionOrder.map((key) => ({
        entries: resolveFitEntries(data[key] ?? []),
        key,
    }));
}

export function createRenderedRows(data: ResolvedFitEntry[]): RenderedFitRow[] {
    return data.flatMap((entry, entryIndex) => {
        if (!shouldExpandCount(entry.categoryId)) {
            return [
                {
                    countLabel: entry.count > 1 ? `x${entry.count}` : null,
                    id: entry.id,
                    key: `${entryIndex}-${entry.id}-stacked`,
                },
            ];
        }

        return Array.from({ length: entry.count }, (_, itemIndex) => ({
            countLabel: null,
            id: entry.id,
            key: `${entryIndex}-${entry.id}-${itemIndex}`,
        }));
    });
}

export function createFitText(
    fitName: string,
    shipId: number,
    sections: ResolvedFitSection[],
) {
    const shipName = resolveTypeName(shipId).en;
    const itemLines = sections.flatMap((section) =>
        section.entries.flatMap((entry) => {
            if (!shouldExpandCount(entry.categoryId)) {
                return entry.count > 1
                    ? [`${entry.name.en} x${entry.count}`]
                    : [entry.name.en];
            }

            return Array.from({ length: entry.count }, () => entry.name.en);
        }),
    );

    return [`[${shipName}, ${fitName}]`, ...itemLines].join("\n");
}
