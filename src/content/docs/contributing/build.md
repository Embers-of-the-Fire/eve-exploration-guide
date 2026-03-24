---
title: 构建与校验
description: 本地开发环境、常用命令，以及提交前必须完成的校验流程。
---

## 前提条件

- Node.js 和 `pnpm`
- `uv`

安装前端依赖：

```bash
pnpm install
```

> EVE 文档数据生成器位于 `packages/eve-docs-generator/`，通过 `uv run`
> 作为独立 Python 项目执行。
>
> 本地化模糊检索工具位于 `packages/eve-loc-fuzz/`，同样通过 `uv`
> 作为独立 Python 项目执行。

## 常用命令

- `pnpm dev`：启动 Astro 开发服务器。
- `pnpm build`：构建站点。
- `pnpm format`：运行 Prettier。
- `pnpm lint`：运行 Biome 和文档 remark lint。
- `pnpm check`：运行 Astro 类型检查。
- `pnpm extract:extension-ids`：触发构建并刷新
  `src/generated/extension-ids.json`。
- `pnpm generate:eve-docs-data`：基于 inspect manifest 和 TQ
  源工作区生成最小化数据。
- `pnpm loc:fuzz -- <query>`：在本地化 pickle 缓存中按子串检索文本。

## 查询本地化文本

如果你需要快速确认某段文本对应的本地化 `loc_id`，可以使用
`packages/eve-loc-fuzz/` 提供的检索工具：

```bash
pnpm loc:fuzz -- warp --lang en-us
pnpm loc:fuzz -- "跃迁" --lang zh
pnpm loc:fuzz -- ship --lang en-us --workspace /path/to/workspace --limit 20
```

说明：

- 必须显式传入至少一个 `--lang`；可以重复传入 `--lang`
  来同时查询多个语言包。
- 默认工作区是仓库根目录下的 `./workspace`。
- 工具会优先读取 `<workspace>/.cache/resources/localizationfsd/`；
  如果该目录不存在，会回退到当前仓库实际使用的
  `<workspace>/.cache/eve-docs-generator/resources/localizationfsd/`。
- 也可以用 `--localization-dir` 直接指定 pickle 所在目录。
- 匹配规则是简单的子串包含关系，不做 Levenshtein
  之类的相似度计算。
- 默认大小写不敏感；需要严格区分大小写时可传入
  `--case-sensitive`。
- 输出内容为 `loc_id` 和本地化文本，并按文本长度升序排序。

## 刷新 EVE 文档数据

当你新增或修改了 `EveType`、`EveLocText`、`EveIcon` 的调用点时，需要额外同步一次生成数据：

```bash
pnpm extract:extension-ids
pnpm generate:eve-docs-data --workspace /path/to/tq-source-workspace
```

说明：

- `--workspace` 目录应当包含 `resfileindex.txt`，以及 `fsd/`
  目录或直接放置的 FSD 文件。
- 也可以通过环境变量 `EVE_DOCS_WORKSPACE` 提供工作区；
  生成器会在 Python 侧读取 `.env`。
- 原始资源缓存默认写到
  `<workspace>/.cache/eve-docs-generator/resources`；也可以通过
  `--resource-cache-dir`、`--workspace-cache-dir`、
  `EVE_DOCS_RESOURCE_CACHE_DIR` 或 `EVE_DOCS_WORKSPACE_CACHE_DIR`
  覆盖。
- FSD 文件当前支持 `json`、`msgpack`、`mpk`、`fsdbinary` 等本地结构化格式。
- 当前生成器只支持 `tq`，并默认使用
  `https://resources.eveonline.com/` 解析 `resfileindex.txt`
  中的资源 URL。
- 如果工作区里还有 `start.ini`，生成器会一并记录游戏版本和
  build；没有也可以正常运行。

生成结果会写到：

- `src/generated/extension-ids.json`
- `src/generated/eve/data.ts`
- `src/generated/eve/icons/*.png`
- `src/generated/eve/types/*.png`

生成器只会下载或复用当前文档真正引用到的资源。下载到的原始资源会放在本地缓存目录中，默认位于工作区内，不会被提交到仓库。

## 验证

提交前至少运行：

```bash
pnpm format
pnpm lint
pnpm check
pnpm build
```

如果你修改了 `packages/eve-docs-generator/` 下的 Python 代码，还应额外运行：

```bash
nix-shell -p ruff --run "ruff format packages/eve-docs-generator && ruff check packages/eve-docs-generator"
```
