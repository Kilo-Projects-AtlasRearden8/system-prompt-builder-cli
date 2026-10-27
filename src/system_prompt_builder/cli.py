"""Command-line interface for system_prompt_builder."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .endpoint import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    ChatMessage,
    EndpointClient,
    EndpointConfig,
    MockEndpoint,
    EndpointError,
)
from .models import PromptTemplate
from .store import TemplateStore


def _parse_kwargs(pairs: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise SystemExit(f"Invalid key=value: {pair!r} (use --var KEY=VALUE)")
        key, _, value = pair.partition("=")
        result[key] = value
    return result


def _load_template(store: TemplateStore, name: str) -> PromptTemplate:
    template = store.get(name)
    if template is None:
        raise SystemExit(f"Template not found: {name}")
    return template


def _default_data_dir() -> str:
    return str(Path.home() / ".local" / "share" / "system-prompt-builder")


def cmd_new(args: argparse.Namespace, store: TemplateStore) -> int:
    template = PromptTemplate(
        name=args.name,
        template=args.template,
        variables=_parse_kwargs(args.variable),
        mock_data=_parse_kwargs(args.mock),
        description=args.description or "",
    )
    store.save(template)
    print(f"Saved template '{args.name}' to {store.path_for(args.name)}")
    return 0


def cmd_build(args: argparse.Namespace, store: TemplateStore) -> int:
    template = _load_template(store, args.name)
    overrides = _parse_kwargs(args.variable)
    try:
        rendered = template.render(overrides)
    except ValueError as exc:
        raise SystemExit(str(exc))
    print(rendered)
    return 0


def cmd_preview(args: argparse.Namespace, store: TemplateStore) -> int:
    template = _load_template(store, args.name)
    print(f"Name: {template.name}")
    if template.description:
        print(f"Description: {template.description}")
    vars_ = template.template_variables()
    print(f"Variables: {', '.join(vars_) if vars_ else '(none)'}")
    print(f"Mock data: {template.mock_data if template.mock_data else '(none)'}")
    print("\nTemplate:")
    print(template.template)
    return 0


def cmd_save(args: argparse.Namespace, store: TemplateStore) -> int:
    template = _load_template(store, args.name)
    template.save(args.file)
    print(f"Saved template '{args.name}' to {args.file}")
    return 0


def cmd_test(args: argparse.Namespace, store: TemplateStore) -> int:
    template = _load_template(store, args.name)
    overrides = _parse_kwargs(args.variable)
    rendered = template.render(overrides)

    base_url = args.endpoint or DEFAULT_BASE_URL
    model = args.model or DEFAULT_MODEL

    if args.mock_endpoint:
        endpoint = MockEndpoint(responses={"mock": "This is a mock live-test response."})
        response = endpoint.chat(
            [
                ChatMessage(role="system", content=rendered),
                ChatMessage(role="user", content="Ping"),
            ]
        )
        print(f"Endpoint: [mock]")
        print(f"Model: mock-model")
    else:
        config = EndpointConfig(
            base_url=base_url, model=model, api_key=args.api_key or ""
        )
        client = EndpointClient(config)
        try:
            response = client.chat(
                [
                    ChatMessage(role="system", content=rendered),
                    ChatMessage(role="user", content="Ping"),
                ]
            )
        except EndpointError as exc:
            raise SystemExit(str(exc))
        print(f"Endpoint: {base_url}")
        print(f"Model: {model}")

    print("\nResponse:")
    print(response.content)
    return 0


def cmd_list(args: argparse.Namespace, store: TemplateStore) -> int:
    names = store.list()
    if not names:
        print("(no templates saved)")
        return 0
    for name in names:
        print(name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="system-prompt-builder",
        description=(
            "Build, preview, save, and live-test system prompts with variables "
            "and mock data against a local OpenAI-compatible endpoint (default Ollama)."
        ),
    )
    parser.add_argument(
        "--data-dir",
        default=_default_data_dir(),
        help="Directory for stored templates (default: ~/.local/share/system-prompt-builder)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Create and save a new prompt template")
    p_new.add_argument("name", help="Template name")
    p_new.add_argument("--template", required=True, help="System prompt template text")
    p_new.add_argument(
        "--variable",
        action="append",
        help="Describe a variable (KEY=description), repeatable",
    )
    p_new.add_argument(
        "--mock",
        action="append",
        help="Default mock value for a variable (KEY=value), repeatable",
    )
    p_new.add_argument("--description", help="Human-readable description")
    p_new.set_defaults(func=cmd_new)

    p_build = sub.add_parser("build", help="Render a template and print the prompt")
    p_build.add_argument("name", help="Template name")
    p_build.add_argument(
        "--variable",
        action="append",
        help="Override a variable (KEY=value), repeatable",
    )
    p_build.set_defaults(func=cmd_build)

    p_preview = sub.add_parser("preview", help="Show a template and its variables")
    p_preview.add_argument("name", help="Template name")
    p_preview.set_defaults(func=cmd_preview)

    p_save = sub.add_parser("save", help="Save a stored template to a JSON file")
    p_save.add_argument("name", help="Template name")
    p_save.add_argument("file", help="Destination JSON file path")
    p_save.set_defaults(func=cmd_save)

    p_test = sub.add_parser("test", help="Live-test a rendered prompt against an endpoint")
    p_test.add_argument("name", help="Template name")
    p_test.add_argument(
        "--endpoint",
        help="Base URL of the OpenAI-compatible endpoint (default Ollama)",
    )
    p_test.add_argument("--model", help="Model name (default: llama3.2)")
    p_test.add_argument(
        "--api-key",
        help="API key (usually empty for Ollama)",
    )
    p_test.add_argument(
        "--mock-endpoint",
        action="store_true",
        help="Use the built-in mock endpoint instead of the network (no keys, no network)",
    )
    p_test.add_argument(
        "--variable",
        action="append",
        help="Override a variable (KEY=value), repeatable",
    )
    p_test.set_defaults(func=cmd_test)

    p_list = sub.add_parser("list", help="List saved templates")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: Optional[List[str]] = None, store: Optional[TemplateStore] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if store is None:
        store = TemplateStore(args.data_dir)
    return args.func(args, store)


if __name__ == "__main__":
    sys.exit(main())
