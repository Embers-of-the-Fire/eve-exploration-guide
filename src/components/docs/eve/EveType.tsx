import type { CSSProperties } from "react";
import baseStyles from "../inline/InlineReference.module.css";
import styles from "./EveReference.module.css";
import InlinePopover from "./InlinePopover";
import {
    formatEveRef,
    formatMissingLabel,
    getIconEntry,
    getTypeEntry,
    resolveLocalization,
    resolveOptionalLocalization,
    shouldShowMissingDataNote,
} from "./data";

export interface EveTypeProps {
    size?: number | string;
    typeId: number;
}

function toCssSize(value: number | string): string {
    return typeof value === "number" ? `${value}px` : value;
}

function describeImageSource(typeData: ReturnType<typeof getTypeEntry>) {
    if (!typeData?.imageSource) {
        return null;
    }

    if (typeData.imageSource === "icon") {
        return typeData.iconId ? `icon ${typeData.iconId}` : "icon";
    }

    if (typeData.imageSource === "graphic-blueprint") {
        return typeData.graphicId
            ? `graphic ${typeData.graphicId} (blueprint)`
            : "graphic (blueprint)";
    }

    return typeData.graphicId ? `graphic ${typeData.graphicId}` : "graphic";
}

export default function EveType({ size = 16, typeId }: EveTypeProps) {
    const typeData = getTypeEntry(typeId);
    const name = typeData
        ? resolveLocalization(typeData.typeNameLocId, "type", typeId)
        : {
              en: formatMissingLabel("type", typeId),
              missing: true,
              zhCN: formatMissingLabel("type", typeId),
          };
    const description = resolveOptionalLocalization(typeData?.descriptionLocId);
    const group = resolveOptionalLocalization(typeData?.groupNameLocId);
    const category = resolveOptionalLocalization(typeData?.categoryNameLocId);
    const metaGroup = resolveOptionalLocalization(typeData?.metaGroupNameLocId);
    const resolvedSize = toCssSize(size);
    const iconStyle: CSSProperties = {
        height: resolvedSize,
        width: resolvedSize,
    };
    const overlaySize =
        typeof size === "number"
            ? `${Math.max(12, Math.min(16, size * 0.5))}px`
            : "0.6em";
    const overlayStyle: CSSProperties = {
        height: overlaySize,
        width: overlaySize,
    };
    const imageSource = describeImageSource(typeData);
    const metaGroupIcon = getIconEntry(typeData?.metaGroupIconId ?? -1);
    const showMissingNote = shouldShowMissingDataNote([
        !typeData,
        name.missing,
        description?.missing,
        group?.missing,
        category?.missing,
        metaGroup?.missing,
        !typeData?.imageSrc,
    ]);

    return (
        <InlinePopover
            ariaLabel={`${name.zhCN} / ${name.en}`}
            className={styles.inlineReference}
            dataRef={formatEveRef("type", typeId)}
            id={`eve-type-${typeId}`}
            label={
                <strong className={`${baseStyles.label} ${styles.inlineLabel}`}>
                    {name.zhCN}
                </strong>
            }
            prefix={
                <span className={styles.typeImage}>
                    {typeData?.imageSrc ? (
                        <img
                            alt={name.zhCN}
                            className={`${baseStyles.icon} ${styles.typeImageMain}`}
                            decoding="async"
                            src={typeData.imageSrc}
                            style={iconStyle}
                        />
                    ) : (
                        <span
                            aria-hidden="true"
                            className={`${styles.missingIcon} ${styles.typeImageMain}`}
                            style={iconStyle}
                        >
                            ?
                        </span>
                    )}
                    {metaGroupIcon ? (
                        <span className={styles.typeOverlay}>
                            <img
                                alt={
                                    metaGroup?.zhCN ??
                                    metaGroup?.en ??
                                    "Meta group"
                                }
                                className={styles.typeOverlayIcon}
                                decoding="async"
                                src={metaGroupIcon.src}
                                style={overlayStyle}
                            />
                        </span>
                    ) : null}
                </span>
            }
        >
            <span className={styles.detailGrid}>
                <span className={styles.section}>
                    <span className={baseStyles.popoverTable}>
                        <span className={baseStyles.popoverRow}>
                            <span className={baseStyles.popoverLabel}>
                                NAME.ZH-CN
                            </span>
                            <span className={baseStyles.popoverValue}>
                                {name.zhCN}
                            </span>
                        </span>
                        <span className={baseStyles.popoverRow}>
                            <span className={baseStyles.popoverLabel}>
                                NAME.EN
                            </span>
                            <span className={baseStyles.popoverValue}>
                                {name.en}
                            </span>
                        </span>
                    </span>
                </span>
                {description ? (
                    <span className={styles.section}>
                        <span className={baseStyles.popoverTable}>
                            <span className={baseStyles.popoverRow}>
                                <span className={baseStyles.popoverLabel}>
                                    DESC.ZH-CN
                                </span>
                                <span className={baseStyles.popoverValue}>
                                    {description.zhCN}
                                </span>
                            </span>
                            <span className={baseStyles.popoverRow}>
                                <span className={baseStyles.popoverLabel}>
                                    DESC.EN
                                </span>
                                <span className={baseStyles.popoverValue}>
                                    {description.en}
                                </span>
                            </span>
                        </span>
                    </span>
                ) : null}
                <span className={styles.metaList}>
                    <span className={styles.metaRow}>
                        <span className={styles.metaLabel}>Type ID</span>
                        <span className={styles.metaValue}>{typeId}</span>
                    </span>
                    {group ? (
                        <span className={styles.metaRow}>
                            <span className={styles.metaLabel}>Group</span>
                            <span className={styles.metaValue}>
                                {group.zhCN} / {group.en}
                                {typeData?.groupId
                                    ? ` (${typeData.groupId})`
                                    : null}
                            </span>
                        </span>
                    ) : null}
                    {category ? (
                        <span className={styles.metaRow}>
                            <span className={styles.metaLabel}>Category</span>
                            <span className={styles.metaValue}>
                                {category.zhCN} / {category.en}
                                {typeData?.categoryId
                                    ? ` (${typeData.categoryId})`
                                    : null}
                            </span>
                        </span>
                    ) : null}
                    {metaGroup ? (
                        <span className={styles.metaRow}>
                            <span className={styles.metaLabel}>Meta</span>
                            <span className={styles.metaValue}>
                                {metaGroup.zhCN} / {metaGroup.en}
                                {typeData?.metaGroupId
                                    ? ` (${typeData.metaGroupId})`
                                    : null}
                            </span>
                        </span>
                    ) : null}
                    {imageSource ? (
                        <span className={styles.metaRow}>
                            <span className={styles.metaLabel}>Image</span>
                            <span className={styles.metaValue}>
                                {imageSource}
                            </span>
                        </span>
                    ) : null}
                </span>
            </span>
            {showMissingNote ? (
                <span className={styles.missingNote}>
                    Missing generated TQ type data or copied assets. Run the EVE
                    docs generator after updating doc references.
                </span>
            ) : null}
        </InlinePopover>
    );
}
