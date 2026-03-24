import type { Sidebar } from "./sidebar.type";

export const contributingSidebar: Sidebar = [
    {
        label: "贡献与开发",
        items: [
            {
                label: "贡献指南",
                link: "/contributing/",
            },
            {
                label: "提交流程",
                link: "/contributing/workflow/",
            },
        ],
    },
    {
        label: "构建与校验",
        items: [
            {
                label: "构建步骤",
                link: "/contributing/build/",
            },
            {
                label: "扩展组件",
                link: "/contributing/extensions/",
            },
        ],
    },
    {
        label: "改动日志",
        link: "/contributing/changelog/",
    },
];
