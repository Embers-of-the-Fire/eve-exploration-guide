// @ts-check
import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";
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

const starlightPlugins = [
    starlightBlog({
        authors,
        title: "Blog",
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
            title: "Maintained by the EVE Exploration Guide team",
            href: siteUrl,
            description:
                "This site uses a tailored Starlight baseline modeled after pdxdoc-next.",
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
const siteConfig = process.env.SITE_URL ? { site: process.env.SITE_URL } : {};

// https://astro.build/config
export default defineConfig({
    ...siteConfig,
    markdown: {
        rehypePlugins,
    },
    integrations: [
        starlight({
            components: {
                MarkdownContent:
                    "./src/components/overrides/MarkdownContent.astro",
                Pagination: "./src/components/overrides/Pagination.astro",
            },
            title: "EVE Exploration Guide",
            plugins: starlightPlugins,
        }),
    ],
});
