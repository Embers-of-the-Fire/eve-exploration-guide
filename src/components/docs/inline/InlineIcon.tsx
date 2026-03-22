import type { CSSProperties } from "react";
import styles from "./InlineReference.module.css";

export interface InlineIconProps {
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
    id,
    src,
    alt,
    size,
    rounded = false,
}: InlineIconProps) {
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
