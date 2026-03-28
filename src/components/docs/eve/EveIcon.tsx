import type { CSSProperties } from "react";
import {
    registerEveIconId,
    resolveExtensionIdRenderMeta,
    type WithExtensionIdSourceProps,
} from "@astro-extension-ids/runtime";
import baseStyles from "../inline/InlineReference.module.css";
import styles from "./EveReference.module.css";
import { formatEveRef, formatMissingLabel, getIconEntry } from "./data";

export interface EveIconProps extends WithExtensionIdSourceProps {
    alt?: string;
    iconId: number;
    size: number | string;
}

function toCssSize(value: number | string): string {
    return typeof value === "number" ? `${value}px` : value;
}

export default function EveIcon({
    __extensionIdFile,
    __extensionIdLine,
    alt,
    iconId,
    size,
}: EveIconProps) {
    registerEveIconId(
        iconId,
        resolveExtensionIdRenderMeta(__extensionIdFile, __extensionIdLine),
    );

    const iconEntry = getIconEntry(iconId);
    const resolvedSize = toCssSize(size);
    const iconStyle: CSSProperties = {
        height: resolvedSize,
        width: resolvedSize,
    };
    const resolvedAlt = alt ?? `EVE icon ${iconId}`;

    if (!iconEntry) {
        return (
            <span
                aria-label={`${resolvedAlt} (missing generated asset)`}
                className={`${styles.missingIcon} ${styles.inlineAsset}`}
                data-eve-ref={formatEveRef("icon", iconId)}
                role="img"
                style={iconStyle}
                title={formatMissingLabel("icon", iconId)}
            >
                ?
            </span>
        );
    }

    return (
        <img
            alt={resolvedAlt}
            className={`${baseStyles.icon} ${styles.inlineAsset}`}
            data-eve-ref={formatEveRef("icon", iconId)}
            decoding="async"
            src={iconEntry.src}
            style={iconStyle}
        />
    );
}
