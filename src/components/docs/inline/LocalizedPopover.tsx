import type { ReactNode } from "react";
import styles from "./InlineReference.module.css";

export interface LocalizedPopoverProps {
    id: string;
    zhCN: string;
    en: string;
    prefix?: ReactNode;
}

export default function LocalizedPopover({
    id,
    zhCN,
    en,
    prefix,
}: LocalizedPopoverProps) {
    const tooltipId = `${id}-popover`;

    return (
        <button
            aria-describedby={tooltipId}
            aria-label={`${zhCN} / ${en}`}
            className={styles.localized}
            data-extension-id={id}
            data-inline-popover-root=""
            type="button"
        >
            {prefix ? (
                <span className={styles.iconPrefix}>{prefix}</span>
            ) : null}
            <strong className={styles.label}>{zhCN}</strong>
            <span
                className={styles.popover}
                data-inline-popover=""
                id={tooltipId}
                role="tooltip"
            >
                <span className={styles.popoverTable}>
                    <span className={styles.popoverRow}>
                        <span className={styles.popoverLabel}>zh-CN</span>
                        <span className={styles.popoverValue}>{zhCN}</span>
                    </span>
                    <span className={styles.popoverRow}>
                        <span className={styles.popoverLabel}>en</span>
                        <span className={styles.popoverValue}>{en}</span>
                    </span>
                    <span className={styles.popoverRow}>
                        <span className={styles.popoverLabel}>ID</span>
                        <span className={styles.popoverValue}>{id}</span>
                    </span>
                </span>
            </span>
        </button>
    );
}
