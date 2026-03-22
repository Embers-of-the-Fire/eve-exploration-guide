import type { CSSProperties } from "react";
import styles from "./InlineReference.module.css";

export interface InlineImageProps {
    id?: string;
    src: string;
    alt: string;
    width: number | string;
    height?: number | string;
    rounded?: boolean;
}

function toCssSize(value: number | string | undefined): string | undefined {
    if (typeof value === "number") {
        return `${value}px`;
    }

    return value;
}

export default function InlineImage({
    id,
    src,
    alt,
    width,
    height,
    rounded = false,
}: InlineImageProps) {
    const className = rounded
        ? `${styles.image} ${styles.rounded}`
        : styles.image;
    const imageStyle: CSSProperties = {
        height: toCssSize(height) ?? "auto",
        width: toCssSize(width),
    };

    return (
        <img
            alt={alt}
            className={className}
            data-extension-id={id}
            decoding="async"
            src={src}
            style={imageStyle}
        />
    );
}
