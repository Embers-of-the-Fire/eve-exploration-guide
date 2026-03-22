import baseStyles from "../inline/InlineReference.module.css";
import styles from "./EveReference.module.css";
import InlinePopover from "./InlinePopover";
import {
    formatEveRef,
    resolveLocalization,
    shouldShowMissingDataNote,
} from "./data";

export interface EveLocTextProps {
    locId: number;
}

export default function EveLocText({ locId }: EveLocTextProps) {
    const localization = resolveLocalization(locId, "loc", locId);
    const showMissingNote = shouldShowMissingDataNote([localization.missing]);

    return (
        <InlinePopover
            ariaLabel={`${localization.zhCN} / ${localization.en}`}
            dataRef={formatEveRef("loc", locId)}
            id={`eve-loc-${locId}`}
            label={
                <strong className={baseStyles.label}>
                    {localization.zhCN}
                </strong>
            }
        >
            <span className={styles.section}>
                <span
                    className={`${baseStyles.popoverTable} ${styles.compactAttributeTable}`}
                >
                    <span className={baseStyles.popoverRow}>
                        <span className={baseStyles.popoverLabel}>zh-CN</span>
                        <span className={baseStyles.popoverValue}>
                            {localization.zhCN}
                        </span>
                    </span>
                    <span className={baseStyles.popoverRow}>
                        <span className={baseStyles.popoverLabel}>en</span>
                        <span className={baseStyles.popoverValue}>
                            {localization.en}
                        </span>
                    </span>
                    <span className={baseStyles.popoverRow}>
                        <span className={baseStyles.popoverLabel}>LOC ID</span>
                        <span className={baseStyles.popoverValue}>{locId}</span>
                    </span>
                </span>
            </span>
            {showMissingNote ? (
                <span className={styles.missingNote}>
                    Missing generated TQ localization data. Run the EVE docs
                    generator after updating doc references.
                </span>
            ) : null}
        </InlinePopover>
    );
}
