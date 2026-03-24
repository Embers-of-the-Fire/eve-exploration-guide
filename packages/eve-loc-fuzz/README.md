# eve-loc-fuzz

Local `uv` workspace CLIs for substring search across EVE localization data and
type names.

The repository root is a shared `uv` workspace. Both CLIs can be run from the
repository root via `pnpm`, or directly with
`uv run --package eve-loc-fuzz eve-loc-fuzz ...` and
`uv run --package eve-loc-fuzz eve-type-fuzz ...`. They load `.env` files from
the current directory and parent directories, so a repo-root `.env` works
without changing into `packages/eve-loc-fuzz/`.

## Localization search

`pnpm run loc:fuzz -- <query> --lang <lang>`

Localization search looks for `localization_fsd_<lang>.pickle` files in:

- `<workspace>/.cache/resources/localizationfsd/`
- `<workspace>/.cache/eve-docs-generator/resources/localizationfsd/`

`<workspace>` defaults to `./workspace` from the current working directory.

Examples:

```bash
pnpm run loc:fuzz -- warp --lang en-us
pnpm run loc:fuzz -- "\u8d83\u8fc1" --lang zh
pnpm run loc:fuzz -- ship --lang en-us --workspace /absolute/path/to/workspace \
  --limit 20
```

`--lang` is required and may be repeated to search multiple language packs.

Matches are printed in ascending localization text length.

Configuration can come from CLI flags, environment variables, or `.env`:

- `--workspace`, `EVE_LOC_FUZZ_WORKSPACE`, or `EVE_DOCS_WORKSPACE`
- `--localization-dir` or `EVE_LOC_FUZZ_LOCALIZATION_DIR`
- `EVE_DOCS_RESOURCE_CACHE_DIR` or `EVE_DOCS_WORKSPACE_CACHE_DIR`
  when you want to reuse the docs generator cache directly

## Type search

`pnpm run type:fuzz -- <query> --lang <lang>`

Type search reads the same localization pickle files and resolves `typeNameID`
values from the `types` FSD payload in `<workspace>/fsd/`. You can override
that location with `--fsd-dir`.

Examples:

```bash
pnpm run type:fuzz -- drake --lang en-us
pnpm run type:fuzz -- "\u6e21\u9e26" --lang zh
pnpm run type:fuzz -- cruiser --lang en-us \
  --workspace /absolute/path/to/workspace --limit 20
```

Matches are printed in ascending type-name length.

Type search uses the same workspace resolution as localization search and also
accepts `--fsd-dir` or `EVE_LOC_FUZZ_FSD_DIR`.
