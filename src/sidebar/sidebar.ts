import { blogSidebar } from "./blog";
import { changelogSidebar } from "./changelog";
import { docsSidebar } from "./docs";
import type { MetaSidebar, SidebarConf } from "./sidebar.type";

export const sidebar: MetaSidebar = [
  {
    label: "Docs",
    icon: "open-book",
    link: "/guides/",
    id: "docs",
    items: docsSidebar,
  },
  {
    label: "Blog",
    icon: "bars",
    link: "/blog/",
    id: "blog",
    items: blogSidebar,
  },
  {
    label: "Changelog",
    icon: "information",
    link: "/changelog/",
    id: "changelog",
    items: changelogSidebar,
  },
];

export const sidebarTopics: SidebarConf = {
  docs: ["/guides/", "/guides/**/*", "/reference/", "/reference/**/*"],
  blog: ["/blog/", "/blog/**/*"],
  changelog: ["/changelog/", "/changelog/**/*"],
};
