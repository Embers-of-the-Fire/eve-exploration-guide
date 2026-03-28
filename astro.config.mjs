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
import { blogPrefix, coolerCredit, giscusConfig } from "./src/config/site.ts";
import { sidebar, sidebarTopics } from "./src/sidebar/sidebar.ts";

const rehypePlugins = /** @type {any} */ ([rehypeAccessibleEmojis]);
/** @param {string | undefined} value */
const normalizeSiteUrl = (value) => {
    if (!value) return undefined;
    return value.startsWith("http://") || value.startsWith("https://")
        ? value
        : `https://${value}`;
};
const siteUrl = normalizeSiteUrl(
    process.env.SITE_URL ??
        "https://github.com/Embers-of-the-Fire/eve-exploration-guide",
);
const srcDir = fileURLToPath(new URL("./src", import.meta.url));
const extensionIdsDir = fileURLToPath(
    new URL("./packages/astro-extension-ids/src", import.meta.url),
);

const starlightPlugins = [
    starlightBlog({
        authors,
        title: "博客",
        prefix: blogPrefix,
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
    starlightGiscus(giscusConfig),
    starlightCoolerCredit({
        credit: coolerCredit,
    }),
];

// https://astro.build/config
export default defineConfig({
    ...(siteUrl ? { site: siteUrl } : {}),
    vite: {
        resolve: {
            alias: {
                "@": srcDir,
                "@astro-extension-ids": extensionIdsDir,
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
                Footer: "./src/components/overrides/Footer.astro",
                MarkdownContent:
                    "./src/components/overrides/MarkdownContent.astro",
                PageSidebar: "./src/components/overrides/PageSidebar.astro",
            },
            title: "EVE Exploration Guide",
            editLink: {
                baseUrl:
                    "https://github.com/Embers-of-the-Fire/eve-exploration-guide/edit/main/",
            },
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
