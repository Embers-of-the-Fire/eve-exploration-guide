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
];
