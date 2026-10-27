"""Tests for the CLI."""

import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from system_prompt_builder.cli import main
from system_prompt_builder.models import PromptTemplate
from system_prompt_builder.store import TemplateStore


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.store = TemplateStore(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, argv):
        return main(["--data-dir", self.store.data_dir.__str__()] + argv, store=self.store)

    def test_new_build_preview_list(self):
        self.assertEqual(
            self._run(
                [
                    "new",
                    "nurse-bot",
                    "--template",
                    "You are a {role}. Hello {name}.",
                    "--mock",
                    "role=nurse",
                    "--mock",
                    "name=Dylan",
                    "--description",
                    "A nursing assistant prompt.",
                ]
            ),
            0,
        )
        self.assertEqual(self.store.list(), ["nurse-bot"])

        buf = StringIO()
        with patch("sys.stdout", buf):
            self._run(["build", "nurse-bot"])
        self.assertEqual(buf.getvalue(), "You are a nurse. Hello Dylan.\n")

        buf = StringIO()
        with patch("sys.stdout", buf):
            self._run(["build", "nurse-bot", "--variable", "name=Ada"])
        self.assertEqual(buf.getvalue(), "You are a nurse. Hello Ada.\n")

        buf = StringIO()
        with patch("sys.stdout", buf):
            self._run(["preview", "nurse-bot"])
        self.assertIn("Variables: role, name", buf.getvalue())
        self.assertIn("You are a {role}. Hello {name}.", buf.getvalue())

        buf = StringIO()
        with patch("sys.stdout", buf):
            self._run(["list"])
        self.assertIn("nurse-bot", buf.getvalue())

    def test_build_missing_variable_errors(self):
        self.store.save(PromptTemplate(name="m", template="{a} {b}"))
        with self.assertRaises(SystemExit):
            self._run(["build", "m"])

    def test_test_command_uses_mock_endpoint_no_network(self):
        self.store.save(
            PromptTemplate(name="x", template="Say {word}.", mock_data={"word": "hello"})
        )
        # Should not reach the network; uses mock endpoint.
        self.assertEqual(self._run(["test", "x", "--mock-endpoint"]), 0)

    def test_test_command_builds_before_sending(self):
        self.store.save(
            PromptTemplate(name="x", template="Say {word}.", mock_data={"word": "hi"})
        )
        with self.assertRaises(SystemExit):
            self._run(["test", "x"])  # no real endpoint reachable; network error

    def test_save_command_writes_file(self):
        self.store.save(PromptTemplate(name="s", template="{a}", mock_data={"a": "1"}))
        out = Path(self.tmp.name) / "exported.json"
        self.assertEqual(self._run(["save", "s", str(out)]), 0)
        self.assertTrue(out.exists())

    def test_build_unknown_template_errors(self):
        with self.assertRaises(SystemExit):
            self._run(["build", "does-not-exist"])
