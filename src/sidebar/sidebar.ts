import { blogSidebar } from "./blog";
import { contributingSidebar } from "./contributing";
import { docsSidebar } from "./docs";
import type { MetaSidebar, SidebarConf } from "./sidebar.type";

export const sidebar: MetaSidebar = [
    {
        label: "教程",
        icon: "open-book",
        link: "/guides/",
        id: "docs",
        items: docsSidebar,
    },
    {
        label: "博客",
        icon: "bars",
        link: "/blog/",
        id: "blog",
        items: blogSidebar,
    },
    {
        label: "贡献与开发",
        icon: "pencil",
        link: "/contributing/",
        id: "contributing",
        items: contributingSidebar,
    },
];

export const sidebarTopics: SidebarConf = {
    docs: ["/guides/", "/guides/**/*"],
    blog: ["/blog/", "/blog/**/*"],
    contributing: ["/contributing/", "/contributing/**/*"],
};
