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
];
