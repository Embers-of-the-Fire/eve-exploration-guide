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
        label: "站点扩展",
        collapsed: true,
        autogenerate: { directory: "reference" },
    },
    {
        label: "贡献指南",
        link: "https://github.com/Embers-of-the-Fire/eve-exploration-guide/blob/main/CONTRIBUTING.md",
    },
];
