import type { Sidebar } from "./sidebar.type";

export const docsSidebar: Sidebar = [
    {
        label: "Guides",
        link: "/guides/",
    },
    {
        label: "Guide Pages",
        collapsed: false,
        autogenerate: { directory: "guides" },
    },
    {
        label: "Reference",
        collapsed: false,
        autogenerate: { directory: "reference" },
    },
    {
        label: "Contributing",
        link: "https://github.com/Embers-of-the-Fire/eve-exploration-guide/blob/main/CONTRIBUTING.md",
    },
];
