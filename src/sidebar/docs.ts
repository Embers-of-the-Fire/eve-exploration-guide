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
];
