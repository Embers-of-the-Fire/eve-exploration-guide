export interface EveDataMetadata {
    game?: {
        build: string | null;
        version: string | null;
    };
    serverId: string;
    serverName: {
        en: string;
        zhCN: string;
    };
}

export interface EveLocalizationEntry {
    en: string;
    zhCN: string;
}

export interface EveIconEntry {
    iconId: number;
    src: string;
}

export interface EveTypeEntry {
    categoryId?: number;
    categoryNameLocId?: number;
    descriptionLocId?: number;
    graphicId?: number;
    groupId: number;
    groupNameLocId?: number;
    iconId?: number;
    imageSource?: "graphic" | "graphic-blueprint" | "icon";
    imageSrc?: string;
    metaGroupId?: number;
    metaGroupIconId?: number;
    metaGroupNameLocId?: number;
    typeId: number;
    typeNameLocId: number;
}
