import {
    registerTextExtensionId,
    resolveExtensionIdRenderMeta,
    type WithExtensionIdSourceProps,
} from "@astro-extension-ids/runtime";
import LocalizedPopover from "./LocalizedPopover";
import type { LocalizedPopoverProps } from "./LocalizedPopover";

export interface LocalizedTextProps
    extends Omit<LocalizedPopoverProps, "prefix">, WithExtensionIdSourceProps {}

export default function LocalizedText(props: LocalizedTextProps) {
    registerTextExtensionId(
        "LocalizedText",
        props.id,
        resolveExtensionIdRenderMeta(
            props.__extensionIdFile,
            props.__extensionIdLine,
        ),
    );

    return <LocalizedPopover {...props} />;
}
