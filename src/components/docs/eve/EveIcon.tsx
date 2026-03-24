import type { CSSProperties } from "react";
import baseStyles from "../inline/InlineReference.module.css";
import styles from "./EveReference.module.css";
import { formatEveRef, formatMissingLabel, getIconEntry } from "./data";

export interface EveIconProps {
    alt?: string;
    iconId: number;
    size: number | string;
}

function toCssSize(value: number | string): string {
    return typeof value === "number" ? `${value}px` : value;
}

export default function EveIcon({ alt, iconId, size }: EveIconProps) {
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
                className={styles.missingIcon}
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
            className={baseStyles.icon}
            data-eve-ref={formatEveRef("icon", iconId)}
            decoding="async"
            src={iconEntry.src}
            style={iconStyle}
        />
    );
}
