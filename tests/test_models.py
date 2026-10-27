"""Tests for the prompt template model."""

import unittest
from pathlib import Path
import tempfile

from system_prompt_builder.endpoint import ChatMessage, MockEndpoint
from system_prompt_builder.models import PromptTemplate


class PromptTemplateTests(unittest.TestCase):
    def test_template_variables_order(self):
        t = PromptTemplate(
            name="x",
            template="Hello {name}, you are a {role}. {name} again.",
        )
        self.assertEqual(t.template_variables(), ["name", "role"])

    def test_render_uses_mock_data_defaults(self):
        t = PromptTemplate(
            name="x",
            template="Hi {name}, role is {role}.",
            mock_data={"name": "Dylan", "role": "author"},
        )
        self.assertEqual(t.render(), "Hi Dylan, role is author.")

    def test_render_override_mock_data(self):
        t = PromptTemplate(
            name="x",
            template="Hi {name}, role is {role}.",
            mock_data={"name": "Dylan", "role": "author"},
        )
        self.assertEqual(t.render({"name": "Ada"}), "Hi Ada, role is author.")

    def test_render_missing_variable_raises(self):
        t = PromptTemplate(name="x", template="Hi {name}, role is {role}.")
        with self.assertRaises(ValueError) as ctx:
            t.render({})
        self.assertIn("name", str(ctx.exception))
        self.assertIn("role", str(ctx.exception))

    def test_missing_variables(self):
        t = PromptTemplate(
            name="x",
            template="{a} {b} {c}",
            mock_data={"a": "1"},
        )
        self.assertEqual(t.missing_variables({}), ["b", "c"])
        self.assertEqual(t.missing_variables({"b": "2"}), ["c"])

    def test_round_trip_dict(self):
        t = PromptTemplate(
            name="n",
            template="{a} {b}",
            variables={"a": "desc a"},
            mock_data={"a": "1", "b": "2"},
            description="d",
        )
        t2 = PromptTemplate.from_dict(t.to_dict())
        self.assertEqual(t2.name, "n")
        self.assertEqual(t2.template, "{a} {b}")
        self.assertEqual(t2.mock_data, {"a": "1", "b": "2"})
        self.assertEqual(t2.render(), "1 2")

    def test_save_and_load_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "tpl.json"
            t = PromptTemplate(name="n", template="{a}", mock_data={"a": "1"})
            t.save(str(p))
            loaded = PromptTemplate.load(str(p))
            self.assertEqual(loaded.name, "n")
            self.assertEqual(loaded.render(), "1")


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        from system_prompt_builder.store import TemplateStore
        self.store = TemplateStore(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_get_list_delete(self):
        from system_prompt_builder.store import TemplateStore
        t = PromptTemplate(name="alpha", template="{a}", mock_data={"a": "1"})
        self.store.save(t)
        self.assertEqual(self.store.list(), ["alpha"])
        got = self.store.get("alpha")
        self.assertIsNotNone(got)
        self.assertEqual(got.render(), "1")
        self.assertTrue(self.store.delete("alpha"))
        self.assertIsNone(self.store.get("alpha"))
        self.assertEqual(self.store.list(), [])

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.store.get("nope"))

    def test_config_round_trip(self):
        self.store.save_config({"endpoint": "http://x", "model": "m"})
        self.assertEqual(
            self.store.load_config(), {"endpoint": "http://x", "model": "m"}
        )


class EndpointTests(unittest.TestCase):
    def test_mock_endpoint_records_calls(self):
        ep = MockEndpoint(responses={"ping": "pong"})
        resp = ep.chat(
            [
                ChatMessage(role="system", content="You are a helper. ping"),
                ChatMessage(role="user", content="ping"),
            ]
        )
        self.assertEqual(resp.content, "pong")
        self.assertEqual(resp.model, "mock-model")
        self.assertEqual(len(ep.calls), 1)
        self.assertEqual(ep.calls[0][0].role, "system")

    def test_mock_endpoint_default_response(self):
        ep = MockEndpoint()
        resp = ep.chat([ChatMessage(role="user", content="hello there")])
        self.assertIn("mock reply to:", resp.content)


if __name__ == "__main__":
    unittest.main()
