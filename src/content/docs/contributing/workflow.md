---
title: 提交流程
description: 文档修改、生成数据同步和 PR 提交流程说明。
---

构建与校验命令请先参照 [构建与校验](/contributing/build/)。组件 API、示例和生成机制请参照 [扩展组件](/contributing/extensions/)。本页补充文档扩展相关的提交流程，尤其是 EVE 组件引用带来的生成数据同步。

## 纯文档修改

对于中小型的纯文本改动，可以直接修改文档内容并提交 PR。建议在 PR 标题前加上 `[文档]`，方便维护者快速识别。

## 修改或新增 EVE 文档组件调用

如果你的改动涉及以下组件：

- `EveType`
- `EveLocText`
- `EveIcon`
- `EveFit`

除了正文本身，你还需要同步最小化生成数据。推荐流程如下：

1. 修改 `src/content/docs/**/*.md(x)` 中的组件调用。
2. 确认 `EVE_DOCS_WORKSPACE` 已在 shell 或仓库根目录的 `.env` 中配置好，然后运行 `pnpm generate:all` 刷新 manifest 并同步最小化 TQ 数据。
   如只想单独刷新 `src/generated/extension-ids.json`，可以运行 `pnpm build:collect`
   或兼容别名 `pnpm extract:extension-ids`。
   `EveFit` 的 `shipId` 和各分组中的 `data.<section>[].id` 会在收集构建的渲染阶段写入 `eveRefs.typeIds`。
   如需覆盖工作区内默认缓存目录，还可以设置 `EVE_DOCS_RESOURCE_CACHE_DIR`；如果只想临时指定一次工作区，直接运行 `pnpm generate:eve-docs-data -- --workspace /path/to/tq-source-workspace`。
3. 检查并提交以下生成结果：
    - `src/generated/extension-ids.json`
    - `src/generated/eve/data.ts`
    - `src/generated/eve/icons/*.png`
    - `src/generated/eve/types/*.png`
4. 运行验证：
    - `pnpm format`
    - `pnpm lint`
    - `pnpm check`
    - `pnpm build:render`

不要提交整套原始资源，也不要把原始资源复制到 `public/`。站点只需要生成器筛出来的最小化子集。

## 修改生成器或 inspect 集成

如果你改动了：

- `packages/astro-extension-ids/`
- `packages/eve-docs-generator/`
- `src/generated/eve/schema.ts`
- `src/components/docs/eve/`

请额外确认：

- 收集构建输出的 `eveRefs` 结构没有破坏兼容性
- `pnpm generate:eve-docs-data` 仍然能基于 TQ 源工作区生成可用结果
- Python 代码已经过 `ruff format` 和 `ruff check`

对应的 Python 校验命令：

```bash
nix-shell -p ruff --run "ruff format packages/eve-docs-generator && ruff check packages/eve-docs-generator"
```

## PR 提交

开发者提交流程保持不变：

1. Fork 仓库。
2. 在自己的 Fork 中创建 `type/brief-description` 形式的新分支。
3. 提交 PR，并在请求人工审阅前先处理自动审查工具给出的反馈。
