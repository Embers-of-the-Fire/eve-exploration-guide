import {
    eveDataMetadata,
    eveIcons,
    eveLocalizations,
    eveTypes,
} from "@/generated/eve/data";
import {
    eveTypePrices,
    type EveTypePriceDataEntry,
} from "@/generated/eve/type-price-data";
import type {
    EveIconEntry,
    EveLocalizationEntry,
    EveTypeEntry,
} from "@/generated/eve/schema";

export interface ResolvedLocalization {
    en: string;
    missing: boolean;
    zhCN: string;
}

export function formatEveRef(kind: "icon" | "loc" | "type", id: number) {
    return `${kind}:${id}`;
}

export function formatMissingLabel(kind: "icon" | "loc" | "type", id: number) {
    return `${kind}:${id}`;
}

export function getGeneratedDataMetadata() {
    return eveDataMetadata;
}

export function getIconEntry(iconId: number): EveIconEntry | undefined {
    return eveIcons[iconId];
}

export function getLocalizationEntry(
    locId: number | null | undefined,
): EveLocalizationEntry | undefined {
    if (locId === null || locId === undefined) {
        return undefined;
    }

    return eveLocalizations[locId];
}

export function getTypeEntry(typeId: number): EveTypeEntry | undefined {
    return eveTypes[typeId];
}

export function formatTypePriceKey(
    regionId: number,
    typeId: number,
    systemId?: number | null,
) {
    return systemId === null || systemId === undefined
        ? `${regionId}:${typeId}`
        : `${regionId}:${typeId}:${systemId}`;
}

export function getTypePriceEntry(
    regionId: number,
    typeId: number,
    systemId?: number | null,
): EveTypePriceDataEntry | undefined {
    return eveTypePrices[formatTypePriceKey(regionId, typeId, systemId)];
}

export function resolveLocalization(
    locId: number | null | undefined,
    fallbackKind: "loc" | "type",
    fallbackId: number,
): ResolvedLocalization {
    const entry = getLocalizationEntry(locId);
    const fallbackLabel =
        locId === null || locId === undefined
            ? formatMissingLabel(fallbackKind, fallbackId)
            : formatMissingLabel("loc", locId);

    if (entry) {
        const en = entry.en || entry.zhCN || fallbackLabel;
        const zhCN = entry.zhCN || entry.en || fallbackLabel;

        return {
            en,
            missing: false,
            zhCN,
        };
    }

    return {
        en: fallbackLabel,
        missing: true,
        zhCN: fallbackLabel,
    };
}

export function resolveOptionalLocalization(
    locId: number | null | undefined,
): ResolvedLocalization | null {
    if (locId === null || locId === undefined) {
        return null;
    }

    return resolveLocalization(locId, "loc", locId);
}

export function shouldShowMissingDataNote(
    values: Array<boolean | null | undefined>,
) {
    return values.some(Boolean) || getGeneratedDataMetadata() === null;
}
