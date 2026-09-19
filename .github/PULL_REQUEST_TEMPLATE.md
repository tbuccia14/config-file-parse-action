## Description

<!-- What does this PR change, and why? -->

## Related issue

<!-- Link any related issue, e.g. Closes #123 -->

## Type of change

- [ ] `fix` — bug fix (patch release)
- [ ] `feat` — new feature (minor release)
- [ ] `BREAKING CHANGE` — incompatible change (major release)
- [ ] `docs` / `chore` / `ci` / `test` / `refactor` — no release impact

## Test evidence

<!--
Show that the change works as intended, e.g.:
- Output of `uv run --group dev pytest -v` (or the specific new/updated tests)
- Coverage summary (`--cov-report=term-missing`)
- A sample workflow run / config file input and the resulting GITHUB_ENV output,
  for behavior changes not fully covered by unit tests
-->

## Checklist

- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Tests were added or updated in `tests/test_parser.py`
- [ ] `README.md` was updated if documentation/behavior changed
- [ ] `uv run --group dev pytest -v` passes locally
