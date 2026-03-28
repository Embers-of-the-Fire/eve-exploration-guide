import EveType from "./EveType";
import type { EveFitSectionKey } from "./EveFit.sections";
import { createRenderedRows, type ResolvedFitSection } from "./EveFit.shared";
import styles from "./EveFit.module.css";

interface EveFitSectionLabel {
    key: EveFitSectionKey;
    label: string;
}

interface EveFitListProps {
    sections: ResolvedFitSection[];
    sectionLabels: EveFitSectionLabel[];
    name: string;
    shipId: number;
}

export default function EveFitList({
    name,
    sectionLabels,
    sections,
    shipId,
}: EveFitListProps) {
    const labelBySection = new Map(
        sectionLabels.map((section) => [section.key, section.label]),
    );
    const visibleSections = sections
        .map((section) => ({
            key: section.key,
            label: labelBySection.get(section.key) ?? section.key,
            rows: createRenderedRows(section.key, section.entries),
        }))
        .filter((section) => section.rows.length > 0);

    return (
        <section className={styles.panel}>
            <header className={styles.header}>
                <strong className={styles.fitName}>{name}</strong>
                <div aria-hidden="true" className={styles.headerDivider} />
                <div className={styles.shipRow}>
                    <span className={styles.shipType}>
                        <EveType size={14} typeId={shipId} />
                    </span>
                </div>
            </header>
            <div className={styles.sectionList}>
                {visibleSections.map((section) => (
                    <section className={styles.slotSection} key={section.key}>
                        <h3 className={styles.slotTitle}>{section.label}</h3>
                        <ul className={styles.itemList}>
                            {section.rows.map((entry) => (
                                <li className={styles.itemRow} key={entry.key}>
                                    <span className={styles.itemRef}>
                                        <EveType size={20} typeId={entry.id} />
                                    </span>
                                    {entry.countLabel ? (
                                        <span className={styles.countLabel}>
                                            {entry.countLabel}
                                        </span>
                                    ) : null}
                                </li>
                            ))}
                        </ul>
                    </section>
                ))}
            </div>
        </section>
    );
}
