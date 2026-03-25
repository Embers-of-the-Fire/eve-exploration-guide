// @ts-check
import react from "@astrojs/react";
import starlight from "@astrojs/starlight";
import { fileURLToPath } from "node:url";
import { defineConfig } from "astro/config";
import extensionIdsIntegration from "./packages/astro-extension-ids/src/index.ts";
import { rehypeAccessibleEmojis } from "rehype-accessible-emojis";
import starlightBlog from "starlight-blog";
import starlightCoolerCredit from "starlight-cooler-credit";
import starlightGiscus from "starlight-giscus";
import starlightImageZoom from "starlight-image-zoom";
import starlightSidebarTopics from "starlight-sidebar-topics";
import authors from "./author.ts";
import { sidebar, sidebarTopics } from "./src/sidebar/sidebar.ts";

const rehypePlugins = /** @type {any} */ ([rehypeAccessibleEmojis]);
const siteUrl =
    process.env.SITE_URL ??
    "https://github.com/Embers-of-the-Fire/eve-exploration-guide";
const qqGroupUrl = "https://qm.qq.com/q/s1IGiwB7jO";
const srcDir = fileURLToPath(new URL("./src", import.meta.url));

const starlightPlugins = [
    starlightBlog({
        authors,
        title: "博客",
        metrics: {
            readingTime: true,
            words: "total",
        },
    }),
    starlightSidebarTopics(sidebar, {
        exclude: ["/404"],
        topics: sidebarTopics,
    }),
    starlightImageZoom(),
    starlightCoolerCredit({
        credit: {
            title: "南北派专家组 组织汇编",
            href: qqGroupUrl,
            description: "点击加入 QQ 群“南北派专家组”",
        },
    }),
    starlightGiscus({
        repo: "Embers-of-the-Fire/eve-exploration-guide",
        repoId: "R_kgDORtHxWQ",
        category: "Announcements",
        categoryId: "DIC_kwDORtHxWc4C499C",
        inputPosition: "top",
        lazy: true,
    }),
];

// https://astro.build/config
export default defineConfig({
    site: siteUrl,
    vite: {
        resolve: {
            alias: {
                "@": srcDir,
            },
        },
    },
    markdown: {
        rehypePlugins,
    },
    integrations: [
        extensionIdsIntegration(),
        react(),
        starlight({
            components: {
                MarkdownContent:
                    "./src/components/overrides/MarkdownContent.astro",
                Pagination: "./src/components/overrides/Pagination.astro",
            },
            title: "EVE Exploration Guide",
            defaultLocale: "zh-CN",
            locales: {
                root: {
                    label: "简体中文",
                    lang: "zh-CN",
                },
            },
            plugins: starlightPlugins,
        }),
    ],
});
