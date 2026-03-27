import { z } from "astro/zod";

const eveFitI18nSchemaShape = {
    "eveFit.section.cargo": z.string(),
    "eveFit.section.charges": z.string(),
    "eveFit.section.drones": z.string(),
    "eveFit.section.high": z.string(),
    "eveFit.section.low": z.string(),
    "eveFit.section.med": z.string(),
    "eveFit.section.rig": z.string(),
};

// Aggregate project-specific Starlight UI translations here.
export const guideI18nSchemaExtension = z
    .object({
        ...eveFitI18nSchemaShape,
    })
    .partial();
