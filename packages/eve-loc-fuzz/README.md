# eve-loc-fuzz

Local `uv` CLI for substring search across EVE localization pickle files.

It looks for `localization_fsd_<lang>.pickle` files in:

- `<workspace>/.cache/resources/localizationfsd/`
- `<workspace>/.cache/eve-docs-generator/resources/localizationfsd/`

`<workspace>` defaults to `./workspace` from the current working directory.

Examples:

```bash
pnpm run loc:fuzz -- warp --lang en-us
pnpm run loc:fuzz -- "\u8d83\u8fc1" --lang zh
pnpm run loc:fuzz -- ship --workspace /absolute/path/to/workspace --limit 20
```

Matches are printed in ascending localization text length.
