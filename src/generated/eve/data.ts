import type {
    EveDataMetadata,
    EveIconEntry,
    EveLocalizationEntry,
    EveTypeEntry,
} from "./schema";
import icon24150Url from "./icons/24150.png?url";
import type28665Url from "./types/28665.png?url";
import type28666Url from "./types/28666.png?url";

export const eveGeneratedAt = "2026-03-22T14:24:44.121738+00:00";

export const eveDataMetadata: EveDataMetadata | null = {
    serverId: "tq",
    serverName: {
        en: "Tranquility",
        zhCN: "宁静",
    },
    game: {
        build: "3221584",
        version: "23.02",
    },
};

export const eveLocalizations: Record<number, EveLocalizationEntry> = {
    63544: { en: "Ship", zhCN: "舰船" },
    63547: { en: "Blueprint", zhCN: "蓝图" },
    63655: { en: "Battleship Blueprint", zhCN: "战列舰蓝图" },
    64268: { en: "Marauder", zhCN: "掠夺舰" },
    66673: { en: "Tech II", zhCN: "二级科技" },
    71714: { en: "Vargur Blueprint", zhCN: "恶狼级蓝图" },
    94919: {
        en: "Geared toward versatility and prolonged deployment in hostile environments, Marauders represent the cutting edge in today’s warship technology. While being thick-skinned, hard-hitting monsters on their own, they are also able to use Bastion technology. Similar in effect to capital reconfiguration technology, when activated the Bastion module provides huge bonuses to firepower and the ability to withstand enormous amounts of punishment, at the cost of being stationary.",
        zhCN: "旨在成为多用途且能够长时间部署于敌方区域的掠夺舰，代表了当代战舰科技的最前沿。它不仅皮糙肉厚、火力凶猛，还能够使用堡垒科技克敌制胜。这种科技与旗舰的配置技术类似，开启堡垒装备后，舰船的火力大幅提高，同时能够承受巨额伤害，但代价是无法移动。",
    },
    106452: { en: "Vargur", zhCN: "恶狼级" },
    297962: { en: "Silent Battleground", zhCN: "寂静的战场" },
};

export const eveIcons: Record<number, EveIconEntry> = {
    24150: { iconId: 24150, src: icon24150Url },
};

export const eveTypes: Record<number, EveTypeEntry> = {
    28665: {
        groupId: 900,
        groupNameLocId: 64268,
        categoryId: 6,
        categoryNameLocId: 63544,
        descriptionLocId: 94919,
        graphicId: 3354,
        metaGroupId: 2,
        metaGroupNameLocId: 66673,
        metaGroupIconId: 24150,
        imageSource: "graphic",
        imageSrc: type28665Url,
        typeId: 28665,
        typeNameLocId: 106452,
    },
    28666: {
        groupId: 107,
        groupNameLocId: 63655,
        categoryId: 9,
        categoryNameLocId: 63547,
        graphicId: 3354,
        metaGroupId: 2,
        metaGroupNameLocId: 66673,
        metaGroupIconId: 24150,
        imageSource: "graphic-blueprint",
        imageSrc: type28666Url,
        typeId: 28666,
        typeNameLocId: 71714,
    },
};
