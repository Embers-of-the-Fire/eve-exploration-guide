import LocalizedPopover from "./LocalizedPopover";
import type { LocalizedPopoverProps } from "./LocalizedPopover";

export interface LocalizedTextProps extends Omit<
    LocalizedPopoverProps,
    "prefix"
> {}

export default function LocalizedText(props: LocalizedTextProps) {
    return <LocalizedPopover {...props} />;
}
