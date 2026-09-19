# Copilot Instructions

## Project Overview

This is a **composite GitHub Action** written in Python that parses JSON or YAML configuration files and exports all key-value pairs to `GITHUB_ENV`.

- **Entry point:** `src/parser.py`
- **Action definition:** `action.yml`
- **Runtime:** Python 3.12, managed via [`uv`](https://github.com/astral-sh/uv)
- **Tests:** pytest (`tests/test_parser.py`), fixtures in `tests/fixtures/`

## Key Behaviour

- All variables are written to `GITHUB_ENV`; they are available as environment variables (`$VAR_NAME`) in subsequent steps — **not** as step outputs (`${{ steps.X.outputs.VAR }}`)
- Nested structures are **flattened with underscores**: `database.host` → `DATABASE_HOST`
- Keys are **uppercased**; hyphens (`-`) and dots (`.`) become underscores (`_`)
- List items are indexed: `features[0]` → `FEATURES_0`
- An optional `prefix` is prepended to all variable names: `APP` + `DATABASE_HOST` → `APP_DATABASE_HOST`
- Multiline values use the [GitHub heredoc delimiter syntax](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/passing-information-between-jobs#multiline-strings)

## Repository Structure

```
src/parser.py          # Core parsing logic (flatten, parse_file, write_variables, main)
action.yml             # GitHub Action definition (inputs, composite steps)
tests/test_parser.py   # pytest test suite
tests/fixtures/        # Sample JSON/YAML files used by tests
README.md              # Action documentation (edited directly)
```

## Development

```bash
# Run tests
uv run --group dev pytest -v
```

## Conventions

### Commits — Conventional Commits (enforced by Commitlint)

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

Supported types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`

Version impact:
- `feat` → minor bump
- `fix`, `perf`, `refactor`, `revert` → patch bump
- `BREAKING CHANGE` footer or `!` suffix → major bump

### Pull Requests

- Create a branch directly in the central repo (preferred) or use a fork
- For complex changes, describe the changes in the PR description with links to test results
- Use Draft PRs when not yet ready for review

### Security

- Do not hardcode secrets or credentials in any file

## Adding New Features

1. Modify `src/parser.py` for logic changes
2. Update `action.yml` if new inputs are added
3. Update `README.md` directly if documentation changes are needed
4. Add or update tests in `tests/test_parser.py` with matching fixtures in `tests/fixtures/`
