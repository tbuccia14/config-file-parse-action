# Config File Parser

[![CI](https://github.com/tbuccia14/config-file-parse-action/actions/workflows/ci.yml/badge.svg)](https://github.com/tbuccia14/config-file-parse-action/actions/workflows/ci.yml)
[![Coverage](coverage-badge.svg)](https://github.com/tbuccia14/config-file-parse-action/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A GitHub Action that parses a **JSON or YAML** configuration file and exports every key-value pair to `GITHUB_ENV`, making them available as environment variables in all subsequent steps of the job.

Nested structures are flattened using **underscore notation** (e.g. `database.host` → `DATABASE_HOST`).

---

## Inputs

| Input    | Required | Default    | Description |
|----------|----------|------------|-------------|
| `file`   | ✅ yes   | —          | Path to the JSON or YAML config file |
| `prefix` | ❌ no    | _(empty)_  | Optional prefix for all variable names (e.g. `APP` → `APP_DATABASE_HOST`) |

---

## Usage

### Export a YAML file to environment variables

```yaml
- name: Parse config
  uses: tbuccia14/config-file-parse-action@v1
  with:
    file: config/settings.yml

- name: Use env vars
  run: echo "Host is $DATABASE_HOST"
```

### Export a JSON file to environment variables

```yaml
- name: Parse config
  uses: tbuccia14/config-file-parse-action@v1
  with:
    file: config/settings.json

- name: Use env vars
  run: echo "Host is $DATABASE_HOST"
```

### With a prefix

```yaml
- name: Parse config
  uses: tbuccia14/config-file-parse-action@v1
  with:
    file: config/settings.yml
    prefix: APP

- name: Use prefixed env vars
  run: echo "Host is $APP_DATABASE_HOST"
```

---

## Key naming rules

- All keys are **uppercased**
- Hyphens (`-`) and dots (`.`) are replaced with underscores (`_`)
- Nested keys are joined with underscores: `database.host` → `DATABASE_HOST`
- List items use their index: `features[0]` → `FEATURES_0`
- An optional `prefix` is prepended: `APP` + `DATABASE_HOST` → `APP_DATABASE_HOST`

---

## Example

With the following `config.yml`:

```yaml
app:
  name: my-service
  version: "1.0.0"
  replicas: 3

database:
  host: db.example.com
  port: 5432

features:
  - auth
  - notifications
```

The following environment variables are set in all subsequent steps:

```
APP_NAME=my-service
APP_VERSION=1.0.0
APP_REPLICAS=3
DATABASE_HOST=db.example.com
DATABASE_PORT=5432
FEATURES_0=auth
FEATURES_1=notifications
```

---

## Development

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run tests
uv run --group dev pytest -v
```

---

## 🤝 Contributing

Do please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this repository.
