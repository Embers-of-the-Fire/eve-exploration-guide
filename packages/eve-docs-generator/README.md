# eve-docs-generator

Local `uv` workspace helper for generating the minimal checked-in EVE docs
dataset used by the MDX React components in this repository.

From the repository root, run it with `pnpm run generate:eve-docs-data -- ...`
or directly with `uv run --package eve-docs-generator eve-docs-generator ...`.

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

HTTP downloads also honor `HTTPS_PROXY` / `HTTP_PROXY` when either variable is
set.

If your proxy re-signs TLS traffic and you need to skip certificate validation
for these downloads, set `EVE_DOCS_SKIP_SSL_VERIFY=true`.
