# EVE Exploration Guide

This site is an Astro + Starlight documentation project with a tailored baseline modeled after `../pdxdoc-next`.

## Structure

Content lives under `src/content/docs/`:

- `guides/` for primary documentation
- `reference/` for terse reference material
- `blog/` for dated posts powered by `starlight-blog`
- `changelog/` for release notes and historical updates

Sidebar topic group definitions live in `src/sidebar/`.

## Giscus

Giscus is partially wired to the real target repository:

- repo: `Embers-of-the-Fire/eve-exploration-guide`
- repo ID: `R_kgDORtHxWQ`
- category name: `Ideas`

The remaining value is `GISCUS_CATEGORY_ID`.

Once the matching category exists for this repository, set:

- `GISCUS_CATEGORY_ID`

`SITE_URL` is optional. If set, Astro can emit absolute metadata and sitemap URLs. If unset, the site still builds normally.

## Included extras

The current baseline includes:

- `starlight-image-zoom`
- `starlight-giscus` when `GISCUS_CATEGORY_ID` is set
- `starlight-cooler-credit`
- `rehype-accessible-emojis`

## Commands

All commands run from the project root:

- `pnpm install`
- `pnpm dev`
- `pnpm build`
- `pnpm preview`
- `pnpm check`
