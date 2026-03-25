import type { Sidebar } from "./sidebar.type";

export const docsSidebar: Sidebar = [
    {
        label: "前言",
        link: "/guides/",
    },
    {
        label: "序言",
        collapsed: true,
        autogenerate: { directory: "guides/preface" },
    },
    {
        label: "快速指南",
        link: "/guides/quick-guide",
    },
    {
        label: "入门探索",
        items: [
            {
                label: "扫描操作",
                link: "/guides/basic-exploration/probing",
            },
            {
                label: "信号类型",
                link: "/guides/basic-exploration/site-types",
            },
            {
                label: "扫描地区",
                items: [
                    {
                        label: "总览",
                        link: "/guides/basic-exploration/areas",
                    },
                    {
                        label: "虫洞",
                        link: "/guides/basic-exploration/areas/wormhole",
                    },
                    {
                        label: "无人机区",
                        link: "/guides/basic-exploration/areas/drone-region",
                    },
                ],
            },
            {
                label: "破译",
                link: "/guides/basic-exploration/hacking",
            },
        ],
    },
    {
        label: "装备",
        items: [
            {
                label: "概述",
                link: "/guides/equipment/",
            },
            {
                label: "飞船",
                link: "/guides/equipment/ships",
            },
            {
                label: "高槽",
                link: "/guides/equipment/high-slots",
            },
            {
                label: "中槽",
                link: "/guides/equipment/med-slots",
            },
            {
                label: "低槽",
                link: "/guides/equipment/low-slots",
            },
            {
                label: "改装件",
                link: "/guides/equipment/rig-slots",
            },
            {
                label: "脑插",
                link: "/guides/equipment/implants",
            },
            {
                label: "其他",
                link: "/guides/equipment/misc",
            },
            {
                label: "技能",
                link: "/guides/equipment/skills",
            },
        ],
    },
    {
        label: "生存",
        collapsed: true,
        items: [
            {
                label: "基本设置",
                link: "/guides/survival/setting",
            },
            {
                label: "技巧",
                link: "/guides/survival/tricks",
            },
            {
                label: "逃跑",
                link: "/guides/survival/escape",
            }
        ]
    },
    {
        label: "进阶",
        autogenerate: { directory: "guides/advance" },
    },
    {
        label: "高阶技巧",
        autogenerate: { directory: "guides/expert" },
    }
];
