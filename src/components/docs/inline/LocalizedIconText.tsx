import {
    registerLocalizedIconTextExtensionIds,
    resolveExtensionIdRenderMeta,
} from "@astro-extension-ids/runtime";
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
    __extensionIdFile,
    __extensionIdLine,
    iconAlt,
    iconId,
    iconSize,
    iconSrc,
    ...textProps
}: LocalizedIconTextProps) {
    registerLocalizedIconTextExtensionIds(
        textProps.id,
        iconId,
        resolveExtensionIdRenderMeta(__extensionIdFile, __extensionIdLine),
    );

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
