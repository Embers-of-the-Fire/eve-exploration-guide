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

如需预热整个 Python workspace 的共享环境，可在仓库根目录执行：

```bash
uv sync --all-packages
```

> EVE 文档数据生成器和本地化模糊检索工具都作为仓库根目录下同一个
> `uv` workspace 的成员包运行。
>
> 仓库根目录下的 `pnpm` 脚本已经封装好了 `uv run --package ...`，
> 不需要先 `cd` 到对应子目录。

## 常用命令

- `pnpm dev`：启动 Astro 开发服务器。
- `pnpm build`：渲染站点；当前等价于 `pnpm build:render`。
- `pnpm build:collect`：执行一次收集构建，并刷新 `src/generated/extension-ids.json`。
- `pnpm build:render`：只基于当前已生成数据渲染站点，不刷新引用 manifest。
- `pnpm build:all`：串联执行收集、EVE 数据生成、市场价格生成和最终渲染；依赖已配置好的 `EVE_DOCS_WORKSPACE`。
- `pnpm format`：运行 Prettier。
- `pnpm lint`：运行 Biome 和文档 remark lint。
- `pnpm check`：运行 Astro 类型检查。
- `pnpm extract:extension-ids`：`pnpm build:collect` 的兼容别名。
- `pnpm generate:eve-docs-data`：基于引用 manifest 和 TQ
  源工作区生成最小化数据。
- `pnpm generate:eve-type-price-data`：基于 `src/generated/eve-type-prices.json`
  由 `packages/eve-docs-generator/` 下的 Python CLI 抓取 EveTycoon
  市场价格，并写出静态价格数据。
- `pnpm generate:all`：串联执行收集构建、EVE 数据生成和市场价格生成；依赖已配置好的 `EVE_DOCS_WORKSPACE`。
- `pnpm loc:fuzz -- <query>`：在本地化 pickle 缓存中按子串检索文本。
- `pnpm type:fuzz -- <query>`：在类型名称中按子串检索 `type_id`。

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
- 也可以通过 `--workspace`、`EVE_LOC_FUZZ_WORKSPACE` 或共享的
  `EVE_DOCS_WORKSPACE` 提供工作区；CLI 会自动读取当前目录或父目录中的
  `.env`，因此仓库根目录下的 `.env` 可以直接复用。
- 工具会优先读取 `<workspace>/.cache/resources/localizationfsd/`；
  如果该目录不存在，会回退到当前仓库实际使用的
  `<workspace>/.cache/eve-docs-generator/resources/localizationfsd/`。
- 也可以用 `--localization-dir` 或 `EVE_LOC_FUZZ_LOCALIZATION_DIR`
  直接指定 pickle 所在目录；如果你已经为生成器配置了
  `EVE_DOCS_RESOURCE_CACHE_DIR` 或 `EVE_DOCS_WORKSPACE_CACHE_DIR`，
  检索工具也会复用对应缓存目录。
- 匹配规则是简单的子串包含关系，不做 Levenshtein
  之类的相似度计算。
- 默认大小写不敏感；需要严格区分大小写时可传入
  `--case-sensitive`。
- 输出内容为 `loc_id` 和本地化文本，并按文本长度升序排序。

## 查询类型名称

如果你需要根据类型名称反查 `type_id`，可以使用
`packages/eve-loc-fuzz/` 中的类型检索入口：

```bash
pnpm type:fuzz -- drake --lang en-us
pnpm type:fuzz -- "渡鸦" --lang zh
pnpm type:fuzz -- cruiser --lang en-us --workspace /path/to/workspace \
  --limit 20
```

说明：

- 必须显式传入至少一个 `--lang`；可以重复传入 `--lang`
  来同时查询多个语言包。
- 默认工作区是仓库根目录下的 `./workspace`。
- 也可以通过 `--workspace`、`EVE_LOC_FUZZ_WORKSPACE` 或共享的
  `EVE_DOCS_WORKSPACE` 提供工作区；CLI 会自动读取当前目录或父目录中的
  `.env`。
- 工具会读取工作区中的 `types` FSD 数据，并用对应语言的
  localization pickle 解析每个类型的 `typeNameID`。
- 默认会优先读取 `<workspace>/fsd/`；如果工作区根目录直接放有
  `types.msgpack`、`types.json` 等 FSD 文件，也会自动识别。
- 也可以用 `--fsd-dir`、`EVE_LOC_FUZZ_FSD_DIR`、`--localization-dir`
  和 `EVE_LOC_FUZZ_LOCALIZATION_DIR` 直接指定类型与本地化数据来源。
- 匹配规则是简单的子串包含关系，不做 Levenshtein
  之类的相似度计算。
- 默认大小写不敏感；需要严格区分大小写时可传入
  `--case-sensitive`。
- 输出内容为 `type_id` 和类型名称，并按名称长度升序排序。

## 刷新 EVE 文档数据

当你新增或修改了 `EveType`、`EveTypePrice`、`EveLocText`、`EveIcon`、`EveFit` 的调用点时，需要额外同步一次生成数据：

先在 shell 或仓库根目录的 `.env` 中设置好 `EVE_DOCS_WORKSPACE`，然后运行：

```bash
pnpm generate:all
```

如果你还想把最终站点也一起渲染出来，可以直接运行：

```bash
pnpm build:all
```

说明：

- `EVE_DOCS_WORKSPACE` 指向的目录应当包含 `resfileindex.txt`，以及 `fsd/`
  目录或直接放置的 FSD 文件。
- `EveTypePrice` 会把 `(regionId, typeId)` 写入 `src/generated/eve-type-prices.json` 中的价格引用清单；
- `EveFit` 会把 `shipId` 和 `data.high[].id`、`data.med[].id`、`data.low[].id`、`data.rig[].id`、`data.charges[].id`、`data.drones[].id`、`data.cargo[].id` 一并写入 `eveRefs.typeIds`；
- `pnpm build:collect` 会在组件实际渲染时读取这些 prop 的求值结果并写入
  manifest；只要收集构建本身能正常求值，`shipId`、`data.<section>[].id`
  以及 `EveTypePrice` 的价格引用都会进入对应清单。
- `pnpm generate:all` / `pnpm build:all` 不转发额外命令行参数；
  其中 EVE 文档生成器和市场价格生成器都会在 Python 侧读取当前目录或父目录中的
  `.env`，因此仓库根目录下的 `.env` 可以直接复用。
- 市场价格生成器会在构建机上直接请求 EveTycoon 的 HTTP API，因此不受浏览器
  CORS 限制；如果你的本地网络环境需要额外代理或证书配置，可以像其他 Python
  下载流程一样通过 shell 或 `.env` 提前准备好对应环境。
- 如果你需要临时覆盖工作区或缓存目录，请直接运行
  `pnpm generate:eve-docs-data -- --workspace /path/to/tq-source-workspace`
  或对应的 `uv run --package eve-docs-generator eve-docs-generator ...`。
- 原始资源缓存默认写到
  `<workspace>/.cache/eve-docs-generator/resources`；也可以通过
  `--resource-cache-dir`、`--workspace-cache-dir`、
  `EVE_DOCS_RESOURCE_CACHE_DIR` 或 `EVE_DOCS_WORKSPACE_CACHE_DIR`
  覆盖。
- FSD 文件当前支持 `json`、`msgpack`、`mpk`、`fsdbinary` 等本地结构化格式。
- 当前生成器只支持 `tq`，并默认使用 `https://resources.eveonline.com/` 解析 `resfileindex.txt` 中的资源 URL。
- 下载器会读取标准代理环境变量；如果你走本地 HTTP 代理（例如 `localhost:7897`），请在 `.env` 中设置 `HTTP_PROXY=http://localhost:7897` 和 `HTTPS_PROXY=http://localhost:7897`。如果代理会重签 HTTPS 证书，还需要额外设置 `SSL_CERT_FILE=/absolute/path/to/proxy-ca.pem`。
- 如果当前 Python 环境没有可用的系统 CA 证书，生成器会自动回退到 `certifi` 提供的公共 CA 集合。
- 如果工作区里还有 `start.ini`，生成器会一并记录游戏版本和 build；没有也可以正常运行。

生成结果会写到：

- `src/generated/extension-ids.json`
- `src/generated/eve-type-prices.json`
- `src/generated/eve/data.ts`
- `src/generated/eve/type-price-data.ts`
- `src/generated/eve/icons/*.png`
- `src/generated/eve/types/*.png`

生成器只会下载或复用当前文档真正引用到的资源。下载到的原始资源会放在本地缓存目录中，默认位于工作区内，不会被提交到仓库。

## 验证

提交前至少运行：

```bash
pnpm format
pnpm lint
pnpm check
pnpm build:render
```

如果你修改了 `packages/eve-docs-generator/` 下的 Python 代码，还应额外运行：

```bash
nix-shell -p ruff --run "ruff format packages/eve-docs-generator && ruff check packages/eve-docs-generator"
```
