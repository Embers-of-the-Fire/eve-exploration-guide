import type { ReactNode } from "react";
import baseStyles from "../inline/InlineReference.module.css";

export interface InlinePopoverProps {
    ariaLabel: string;
    children: ReactNode;
    className?: string;
    dataRef: string;
    id: string;
    label: ReactNode;
    prefix?: ReactNode;
}

export default function InlinePopover({
    ariaLabel,
    children,
    className,
    dataRef,
    id,
    label,
    prefix,
}: InlinePopoverProps) {
    const tooltipId = `${id}-popover`;

    return (
        <button
            aria-describedby={tooltipId}
            aria-label={ariaLabel}
            className={
                className
                    ? `${baseStyles.localized} ${className}`
                    : baseStyles.localized
            }
            data-eve-ref={dataRef}
            type="button"
        >
            {prefix ? (
                <span className={baseStyles.iconPrefix}>{prefix}</span>
            ) : null}
            {label}
            <span className={baseStyles.popover} id={tooltipId} role="tooltip">
                {children}
            </span>
        </button>
    );
}
