# eve-docs-generator

Local `uv`-driven helper for generating the minimal checked-in EVE docs dataset
used by the MDX React components in this repository.

Inputs are a TQ source workspace, not a prebuilt bundle:

- `resfileindex.txt`
- local FSD files (`json`, `msgpack`, `mpk`, `fsdbinary`)
- optional `start.ini`

The workspace must be provided explicitly, either with `--workspace` or via the
`EVE_DOCS_WORKSPACE` environment variable. Downloaded raw resources are cached
under `<workspace>/.cache/eve-docs-generator/resources` by default, and that
location can be overridden with `--resource-cache-dir` /
`--workspace-cache-dir` or the `EVE_DOCS_RESOURCE_CACHE_DIR` environment
variable. The CLI loads `.env` files via `python-dotenv`, so a local `.env` may
contain:

```env
EVE_DOCS_WORKSPACE=/absolute/path/to/tq-source-workspace
EVE_DOCS_RESOURCE_CACHE_DIR=/absolute/path/to/tq-source-workspace/.cache/eve-docs-generator/resources
```
