export const eveFitSectionOrder = [
    "high",
    "med",
    "low",
    "rig",
    "charges",
    "drones",
    "cargo",
] as const;

export type EveFitSectionKey = (typeof eveFitSectionOrder)[number];
