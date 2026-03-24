# 扩展组件说明

当前文档扩展层面向 EVE Online，并由三部分组成：

1. 面向 MDX 暴露的 `tsx` 组件，位于 `src/components/docs/eve/`
2. 基于 Astro remark 的 inspect 集成，位于 `packages/astro-extension-ids/`
3. 基于 `uv` 的本地 Python 生成器，位于 `packages/eve-docs-generator/`

整个流程的目标是只把文档里真正引用到的 TQ 类型、文本和图标同步进仓库，而不是把整套原始客户端资源直接塞进站点源码。

## 组件列表

- `EveType`
- `EveLocText`
- `EveIcon`

## 导入方式

下面的导入路径以 `src/content/docs/reference/extensions.mdx` 为例；如果你的
MDX 文件位于别的目录层级，需要按实际位置调整相对路径。

```mdx
import EveLocText from "../../../components/docs/eve/EveLocText.tsx";
import EveType from "../../../components/docs/eve/EveType.tsx";
```

## `EveType` API

| Prop     | Type               | Default  | Description                                  |
| -------- | ------------------ | -------- | -------------------------------------------- |
| `typeId` | `number`           | Required | TQ `type_id`。                               |
| `size`   | `number \| string` | Required | 内联类型图像尺寸，例如 `16`、`18`、`"1em"`。 |

行为：

- 正文显示类型的 `zh-CN` 名称。
- 前缀图像优先使用 `images/graphics/{graphicId}.png`，其次回退到 `images/icons/{iconId}.png`。
- 如果类型有 Meta Group 图标，会像 EVE-Multitools 一样在页面渲染时叠加一个小角标，而不是写死进图片文件。
- 悬停浮层会展示：
    - `zh-CN` / `en` 名称
    - `zh-CN` / `en` 描述（如果该类型有描述）
        - Group、Category、Meta Group 的本地化文本和 ID
        - 当前使用的图像来源

示例：

```mdx
<EveType typeId={28665} size={18} />
<EveType typeId={28666} size={18} />
```

## `EveLocText` API

| Prop    | Type     | Default  | Description                  |
| ------- | -------- | -------- | ---------------------------- |
| `locId` | `number` | Required | TQ localization message ID。 |

行为：

- 正文只显示 `zh-CN`
- 浮层同时显示 `zh-CN` 和 `en`

示例：

```mdx
<EveLocText locId={297962} />
```

## `EveIcon` API

| Prop     | Type               | Default           | Description                                          |
| -------- | ------------------ | ----------------- | ---------------------------------------------------- |
| `iconId` | `number`           | Required          | TQ icon registry ID。                                |
| `size`   | `number \| string` | Required          | 内联图标尺寸。                                       |
| `alt`    | `string`           | `"EVE icon {id}"` | 替代文本。纯装饰用途时建议在调用侧显式传入空字符串。 |

注意：

- 这里的图标资源最终来自 TQ 源工作区对应的 `iconids` 定义和 `resfileindex.txt`
- 组件本身不会去 `public/` 目录找资源；它只依赖 `src/generated/eve/icons/` 中已生成的文件

## Inspect Manifest

`pnpm extract:extension-ids` 会触发 Astro 构建，并让本地 remark 插件扫描
`src/content/docs/**/*.md(x)` 中的组件调用。

当前会额外输出一个 EVE 专用区段：

```json
{
    "eveRefs": {
        "entries": [],
        "duplicates": [],
        "typeIds": [],
        "locIds": [],
        "iconIds": [],
        "unresolved": []
    }
}
```

提取规则如下：

- `EveType.typeId`
- `EveLocText.locId`
- `EveIcon.iconId`

只接受静态字面量写法，例如：

- `typeId={34}`
- `locId="123456"`
- `iconId={1234}`

如果某个调用点没有提供可静态解析的字面量，插件会把它记录到 `eveRefs.unresolved`。

## 数据生成

inspect 完成后，使用：

```bash
pnpm generate:eve-docs-data --workspace /path/to/tq-source-workspace
```

该命令会进入 `packages/eve-docs-generator/` 并通过
`uv run python -m eve_docs_generator` 执行生成器。默认输入是一个 TQ
源工作区，而不是预构建 bundle。工作区必须显式通过 `--workspace`
或环境变量 `EVE_DOCS_WORKSPACE` 提供；生成器会在 Python 侧加载 `.env`
文件。工作区至少需要：

- `resfileindex.txt`
- `fsd/` 目录，或直接放在目录根下的 FSD 文件

可选输入：

- `start.ini`
- `--resource-cache-dir`
- `--resfileindex`
- `--fsd-dir`

FSD 文件当前支持：

- `json`
- `msgpack`
- `mpk`
- `fsdbinary`

输出文件为：

- `src/generated/eve/data.ts`
- `src/generated/eve/icons/*.png`
- `src/generated/eve/types/*.png`

当前只支持 `tq`。如果没有本地资源缓存，生成器会根据 `resfileindex.txt` 中的 URL 和默认的 TQ 资源服务按需拉取所需资源。

## 回退行为

如果生成数据不存在、缺失某个局部条目，或者你刚写完文档但还没同步源工作区数据：

- `EveType` 会回退为 `type:{typeId}`
- `EveLocText` 会回退为 `loc:{locId}`
- `EveIcon` 会显示占位框

这样做是为了让站点构建和内容编辑保持可用，但这不应该被视为最终发布状态。对于准备合并的文档改动，仍然应当同步并提交最小化的生成数据。
