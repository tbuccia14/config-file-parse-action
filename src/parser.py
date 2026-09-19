#!/usr/bin/env python3
"""
Config File Parser - GitHub Action
Parses JSON or YAML files and exports key-value pairs to GITHUB_ENV.
"""

import json
import os
import sys

import yaml


def flatten(data, prefix="", sep="_"):
    """Recursively flatten nested dicts/lists into a single-level dict with underscore-separated
    keys."""
    items = {}
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{prefix}{sep}{key}" if prefix else key
            items.update(flatten(value, new_key, sep))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            new_key = f"{prefix}{sep}{index}" if prefix else str(index)
            items.update(flatten(value, new_key, sep))
    else:
        items[prefix] = "" if data is None else str(data)
    return items


def parse_file(file_path):
    """Parse a JSON or YAML file and return a Python dict."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".json":
        return json.loads(content)

    if ext in (".yml", ".yaml"):
        return yaml.safe_load(content)

    # No recognized extension — auto-detect by trying JSON first, then YAML
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return yaml.safe_load(content)


def write_variables(variables, target_file):
    """Append key=value pairs to the target file (GITHUB_ENV)."""
    with open(target_file, "a", encoding="utf-8") as f:
        for key, value in variables.items():
            if "\n" in value:
                # Multiline value — use a key-specific delimiter to avoid collision
                delimiter = f"ghadelim_{key}"
                f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{key}={value}\n")


def main():
    # Ensure stdout/stderr can always encode the ✓/→ symbols used below, regardless of the
    # platform's default console encoding (e.g. Windows runners default to cp1252). Guarded
    # with hasattr since redirected streams in tests (e.g. io.StringIO) lack reconfigure().
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    file_path = os.environ.get("INPUT_FILE", "").strip()
    prefix = os.environ.get("INPUT_PREFIX", "").strip().upper()

    # Resolve relative paths against GITHUB_WORKSPACE
    if file_path and not os.path.isabs(file_path):
        workspace = os.environ.get("GITHUB_WORKSPACE", "")
        if workspace:
            file_path = os.path.join(workspace, file_path)

    # Validate inputs
    if not file_path:
        print("::error::Input 'file' is required.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(file_path):
        print(f"::error::File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    target_file = os.environ.get("GITHUB_ENV", "").strip()

    if not target_file:
        print("::error::GITHUB_ENV environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # Parse the config file
    try:
        data = parse_file(file_path)
    except Exception as exc:
        print(f"::error::Failed to parse '{file_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, (dict, list)):
        print(
            "::error::Config file must contain a mapping or list at the top level.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Flatten and apply prefix
    flat = flatten(data)
    variables = {}
    for key, value in flat.items():
        var_name = key.upper().replace("-", "_").replace(".", "_")
        if prefix:
            var_name = f"{prefix}_{var_name}"
        variables[var_name] = value

    # Write to GITHUB_ENV
    write_variables(variables, target_file)

    print(f"✓ Exported {len(variables)} variable(s) → GITHUB_ENV")
    for key, value in variables.items():
        # Mask multiline values in logs
        display = value.replace("\n", "\\n") if "\n" in value else value
        print(f"  {key}={display}")


if __name__ == "__main__":
    main()
