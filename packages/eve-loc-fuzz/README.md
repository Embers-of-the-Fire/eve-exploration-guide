# eve-loc-fuzz

Local `uv` CLIs for substring search across EVE localization data and type
names.

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
