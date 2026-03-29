import { z } from "astro/zod";

const eveFitI18nSchemaShape = {
    "eveFit.section.cargo": z.string(),
    "eveFit.section.charges": z.string(),
    "eveFit.section.drones": z.string(),
    "eveFit.section.high": z.string(),
    "eveFit.section.low": z.string(),
    "eveFit.section.med": z.string(),
    "eveFit.section.rig": z.string(),
    "eveTypePrice.buy": z.string(),
    "eveTypePrice.buyOrders": z.string(),
    "eveTypePrice.buyVolume": z.string(),
    "eveTypePrice.generatedTimestamp.ageWithYears": z.string(),
    "eveTypePrice.generatedTimestamp.ageWithoutYears": z.string(),
    "eveTypePrice.generatedTimestamp.days_one": z.string(),
    "eveTypePrice.generatedTimestamp.days_other": z.string(),
    "eveTypePrice.generatedTimestamp.message": z.string(),
    "eveTypePrice.isk": z.string(),
    "eveTypePrice.sell": z.string(),
    "eveTypePrice.sellOrders": z.string(),
    "eveTypePrice.sellVolume": z.string(),
    "eveTypePrice.unavailable": z.string(),
    "eveTypePrice.generatedTimestamp.years_one": z.string(),
    "eveTypePrice.generatedTimestamp.years_other": z.string(),
};

// Aggregate project-specific Starlight UI translations here.
export const guideI18nSchemaExtension = z
    .object({
        ...eveFitI18nSchemaShape,
    })
    .partial();
