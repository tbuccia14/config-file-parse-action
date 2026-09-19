#!/usr/bin/env python3
"""Unit tests for the config file parser."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

# Make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from parser import flatten, main, parse_file, write_variables

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestFlatten(unittest.TestCase):
    def test_flat_dict(self):
        self.assertEqual(flatten({"key": "value"}), {"key": "value"})

    def test_nested_dict(self):
        data = {"database": {"host": "localhost", "port": 5432}}
        result = flatten(data)
        self.assertEqual(result["database_host"], "localhost")
        self.assertEqual(result["database_port"], "5432")

    def test_list_values(self):
        data = {"features": ["auth", "logs"]}
        result = flatten(data)
        self.assertEqual(result["features_0"], "auth")
        self.assertEqual(result["features_1"], "logs")

    def test_none_value(self):
        result = flatten({"key": None})
        self.assertEqual(result["key"], "")

    def test_deeply_nested(self):
        data = {"a": {"b": {"c": "deep"}}}
        result = flatten(data)
        self.assertEqual(result["a_b_c"], "deep")


class TestParseFile(unittest.TestCase):
    def test_parse_yaml(self):
        data = parse_file(os.path.join(FIXTURES, "config.yml"))
        self.assertIsInstance(data, dict)
        self.assertIn("app", data)
        self.assertEqual(data["app"]["name"], "my-service")

    def test_parse_json(self):
        data = parse_file(os.path.join(FIXTURES, "config.json"))
        self.assertIsInstance(data, dict)
        self.assertIn("database", data)
        self.assertEqual(data["database"]["host"], "db.example.com")

    def test_auto_detect_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("key: value\n")
            fname = f.name
        data = parse_file(fname)
        os.unlink(fname)
        self.assertEqual(data["key"], "value")

    def test_auto_detect_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            json.dump({"key": "value"}, f)
            f.flush()
            data = parse_file(f.name)
        os.unlink(f.name)
        self.assertEqual(data["key"], "value")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parse_file("/nonexistent/path/file.json")

    def test_empty_file(self):
        """An empty YAML file parses to None, which main() should reject."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            fname = f.name
        result = parse_file(fname)
        os.unlink(fname)
        self.assertIsNone(result)

    def test_invalid_yaml_content(self):
        """A YAML file that parses to a plain string (not a dict/list) should return a string."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("just a string\n")
            fname = f.name
        result = parse_file(fname)
        os.unlink(fname)
        self.assertIsInstance(result, str)

    def test_invalid_json_content(self):
        """Malformed JSON should raise an error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            fname = f.name
        with self.assertRaises(Exception):
            parse_file(fname)
        os.unlink(fname)


class TestWriteVariables(unittest.TestCase):
    def test_simple_write(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            fname = f.name

        write_variables({"KEY": "value", "FOO": "bar"}, fname)

        with open(fname) as f:
            content = f.read()

        os.unlink(fname)
        self.assertIn("KEY=value\n", content)
        self.assertIn("FOO=bar\n", content)

    def test_multiline_value(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            fname = f.name

        write_variables({"MULTILINE": "line1\nline2"}, fname)

        with open(fname) as f:
            content = f.read()

        os.unlink(fname)
        self.assertIn("MULTILINE<<ghadelim_MULTILINE\n", content)
        self.assertIn("line1\nline2\n", content)

    def test_multiline_eof_collision(self):
        """Value containing 'EOF' on its own line must not break the heredoc."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            fname = f.name

        write_variables({"CERT": "-----BEGIN-----\nEOF\n-----END-----"}, fname)

        with open(fname) as f:
            content = f.read()

        os.unlink(fname)
        self.assertIn("CERT<<ghadelim_CERT\n", content)
        self.assertIn("EOF\n", content)
        self.assertIn("ghadelim_CERT\n", content)


class TestIntegration(unittest.TestCase):
    """End-to-end tests that simulate the action run."""

    def _run_parser(self, file_path, prefix=""):
        output_file = tempfile.NamedTemporaryFile(mode="w", suffix=".out", delete=False)
        output_file.close()

        env = {
            **os.environ,
            "INPUT_FILE": file_path,
            "INPUT_PREFIX": prefix,
            "GITHUB_ENV": output_file.name,
        }

        import subprocess

        result = subprocess.run(
            ["uv", "run", os.path.join(os.path.dirname(__file__), "..", "src", "parser.py")],
            env=env,
            capture_output=True,
            text=True,
        )

        with open(output_file.name) as f:
            written = f.read()

        os.unlink(output_file.name)
        return result, written

    def test_yaml_to_env(self):
        result, written = self._run_parser(os.path.join(FIXTURES, "config.yml"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("APP_NAME=my-service", written)
        self.assertIn("DATABASE_HOST=db.example.com", written)
        self.assertIn("DATABASE_PORT=5432", written)

    def test_json_to_env(self):
        result, written = self._run_parser(os.path.join(FIXTURES, "config.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DATABASE_HOST=db.example.com", written)

    def test_prefix(self):
        result, written = self._run_parser(os.path.join(FIXTURES, "simple.yml"), prefix="MYAPP")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MYAPP_SIMPLE_KEY=simple_value", written)

    def test_missing_file(self):
        result, _ = self._run_parser("/nonexistent/file.yml")
        self.assertNotEqual(result.returncode, 0)

    def test_relative_file_path_resolved_via_workspace(self):
        """A relative INPUT_FILE should be resolved against GITHUB_WORKSPACE."""
        output_file = tempfile.NamedTemporaryFile(mode="w", suffix=".out", delete=False)
        output_file.close()

        workspace = os.path.dirname(FIXTURES)
        relative_path = os.path.relpath(os.path.join(FIXTURES, "simple.yml"), workspace)

        env = {
            **os.environ,
            "INPUT_FILE": relative_path,
            "INPUT_PREFIX": "",
            "GITHUB_WORKSPACE": workspace,
            "GITHUB_ENV": output_file.name,
        }

        import subprocess

        result = subprocess.run(
            ["uv", "run", os.path.join(os.path.dirname(__file__), "..", "src", "parser.py")],
            env=env,
            capture_output=True,
            text=True,
        )

        with open(output_file.name) as f:
            written = f.read()

        os.unlink(output_file.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SIMPLE_KEY=simple_value", written)


class TestMain(unittest.TestCase):
    """In-process tests for main(), so coverage.py can track execution
    (unlike TestIntegration, which runs the script in a subprocess)."""

    def _run_main(self, env, clear=True):
        """Run main() with the given environment, capturing stdout and exit code."""
        stdout = io.StringIO()
        with patch.dict(os.environ, env, clear=clear):
            with redirect_stdout(stdout):
                try:
                    main()
                    code = 0
                except SystemExit as exc:
                    code = exc.code
        return code, stdout.getvalue()

    def test_missing_input_file(self):
        code, _ = self._run_main({"GITHUB_ENV": tempfile.mktemp()})
        self.assertEqual(code, 1)

    def test_input_file_not_found(self):
        code, _ = self._run_main(
            {
                "INPUT_FILE": "/nonexistent/path/file.yml",
                "GITHUB_ENV": tempfile.mktemp(),
            }
        )
        self.assertEqual(code, 1)

    def test_missing_github_env(self):
        code, _ = self._run_main(
            {
                "INPUT_FILE": os.path.join(FIXTURES, "simple.yml"),
            }
        )
        self.assertEqual(code, 1)

    def test_parse_failure(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            fname = f.name
        code, _ = self._run_main(
            {
                "INPUT_FILE": fname,
                "GITHUB_ENV": tempfile.mktemp(),
            }
        )
        os.unlink(fname)
        self.assertEqual(code, 1)

    def test_invalid_top_level_type(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("just a string\n")
            fname = f.name
        code, _ = self._run_main(
            {
                "INPUT_FILE": fname,
                "GITHUB_ENV": tempfile.mktemp(),
            }
        )
        os.unlink(fname)
        self.assertEqual(code, 1)

    def test_success_yaml(self):
        target = tempfile.mktemp()
        code, stdout = self._run_main(
            {
                "INPUT_FILE": os.path.join(FIXTURES, "config.yml"),
                "GITHUB_ENV": target,
            }
        )
        with open(target) as f:
            written = f.read()
        os.unlink(target)

        self.assertEqual(code, 0)
        self.assertIn("APP_NAME=my-service", written)
        self.assertIn("Exported", stdout)
        self.assertIn("APP_NAME=my-service", stdout)

    def test_success_with_prefix(self):
        target = tempfile.mktemp()
        code, _ = self._run_main(
            {
                "INPUT_FILE": os.path.join(FIXTURES, "simple.yml"),
                "INPUT_PREFIX": "myapp",
                "GITHUB_ENV": target,
            }
        )
        with open(target) as f:
            written = f.read()
        os.unlink(target)

        self.assertEqual(code, 0)
        self.assertIn("MYAPP_SIMPLE_KEY=simple_value", written)

    def test_multiline_value_masked_in_log(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("cert: |\n  line1\n  line2\n")
            fname = f.name
        target = tempfile.mktemp()

        code, stdout = self._run_main(
            {
                "INPUT_FILE": fname,
                "GITHUB_ENV": target,
            }
        )
        os.unlink(fname)
        with open(target) as f:
            written = f.read()
        os.unlink(target)

        self.assertEqual(code, 0)
        self.assertIn("CERT<<ghadelim_CERT\n", written)
        self.assertIn("CERT=line1\\nline2", stdout)

    def test_relative_path_resolved_via_workspace(self):
        workspace = os.path.dirname(FIXTURES)
        relative_path = os.path.relpath(os.path.join(FIXTURES, "simple.yml"), workspace)
        target = tempfile.mktemp()

        code, _ = self._run_main(
            {
                "INPUT_FILE": relative_path,
                "GITHUB_WORKSPACE": workspace,
                "GITHUB_ENV": target,
            }
        )
        with open(target) as f:
            written = f.read()
        os.unlink(target)

        self.assertEqual(code, 0)
        self.assertIn("SIMPLE_KEY=simple_value", written)


if __name__ == "__main__":
    unittest.main()
