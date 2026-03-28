import type { CSSProperties } from "react";
import {
    registerIconExtensionId,
    resolveExtensionIdRenderMeta,
    type WithExtensionIdSourceProps,
} from "@astro-extension-ids/runtime";
import styles from "./InlineReference.module.css";

export interface InlineIconProps extends WithExtensionIdSourceProps {
    id: string;
    src: string;
    alt: string;
    size: number | string;
    rounded?: boolean;
}

function toCssSize(value: number | string): string {
    return typeof value === "number" ? `${value}px` : value;
}

export default function InlineIcon({
    __extensionIdFile,
    __extensionIdLine,
    id,
    src,
    alt,
    size,
    rounded = false,
}: InlineIconProps) {
    registerIconExtensionId(
        "InlineIcon",
        id,
        resolveExtensionIdRenderMeta(__extensionIdFile, __extensionIdLine),
    );

    const resolvedSize = toCssSize(size);
    const className = rounded
        ? `${styles.icon} ${styles.rounded}`
        : styles.icon;
    const iconStyle: CSSProperties = {
        height: resolvedSize,
        width: resolvedSize,
    };

    return (
        <img
            alt={alt}
            className={className}
            data-extension-id={id}
            decoding="async"
            src={src}
            style={iconStyle}
        />
    );
}
