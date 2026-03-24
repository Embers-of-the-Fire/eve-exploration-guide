import InlineIcon from "./InlineIcon";
import type { InlineIconProps } from "./InlineIcon";
import LocalizedPopover from "./LocalizedPopover";
import type { LocalizedTextProps } from "./LocalizedText";

export interface LocalizedIconTextProps extends LocalizedTextProps {
    iconId: string;
    iconSrc: InlineIconProps["src"];
    iconAlt: InlineIconProps["alt"];
    iconSize: InlineIconProps["size"];
}

export default function LocalizedIconText({
    iconAlt,
    iconId,
    iconSize,
    iconSrc,
    ...textProps
}: LocalizedIconTextProps) {
    return (
        <LocalizedPopover
            {...textProps}
            prefix={
                <InlineIcon
                    alt={iconAlt}
                    id={iconId}
                    size={iconSize}
                    src={iconSrc}
                />
            }
        />
    );
}
