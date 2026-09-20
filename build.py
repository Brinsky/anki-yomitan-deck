#!/usr/bin/env python3
"""Assemble the Anki card templates and the test harness from src/ + testcases/.

    python3 build.py

Files in output/ will be removed and recreated.
"""

import json
import re
import shutil
import sys
from pathlib import Path

## File paths

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
TEMPLATES = SRC / "templates"
TESTCASES = ROOT / "testcases"
OUTPUT = ROOT / "output"

## For test harness

# (note type name, src/ path of its Front template, src/ path of its Back template)
NOTE_TYPES = [
    ("written", "templates/front-written.html", "templates/back.html"),
    ("audio", "templates/front-audio.html", "templates/back.html"),
    ("reversed", "templates/front-reverse.html", "templates/back-reverse.html"),
]
TESTING_TEMPLATE = "templates/testing.html"

SAMPLE_FIELDS = TESTCASES / "sample-fields.json"

INCLUDE_RE = re.compile(r"^([ \t]*)<!--\s*@include\s+(\S+)\s*-->[ \t]*$")
DIRECTIVE_RE = re.compile(r"^([ \t]*)<!--\s*@(testcases|note-types)\s*-->[ \t]*$")

# Matches an Anki field placeholder, e.g. {{Word}} or {{FrontSide}}.
FIELD_RE = re.compile(r"\{\{(\w+)\}\}")


class BuildError(Exception):
    pass


def indent_block(text, indent):
    """Prefix every non-blank line of *text* with *indent*.

    Blank lines are left bare so the output has no trailing whitespace.
    """
    if not indent:
        return text
    return "\n".join(indent + line if line.strip() else line for line in text.split("\n"))


def render(rel_path, stack=()):
    """Render a file under src/, resolving @include directives recursively."""
    if rel_path in stack:
        chain = " -> ".join(list(stack) + [rel_path])
        raise BuildError(f"include cycle: {chain}")

    path = SRC / rel_path
    if not path.is_file():
        raise BuildError(f"missing source file: {path.relative_to(ROOT)}")

    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = INCLUDE_RE.match(line)
        if not match:
            out.append(line)
            continue

        indent, target = match.group(1), match.group(2)
        try:
            included = render(target, stack + (rel_path,))
        except BuildError as exc:
            raise BuildError(f"{rel_path}:{lineno}: {exc}") from None
        out.append(indent_block(included, indent))

    return "\n".join(out).rstrip("\n")


def discover_templates():
    """Return [(output filename, src/ path)] for every file in src/templates/
    except TESTING_TEMPLATE, sorted by filename.

    Each one is rendered and written to output/ under its own name -- adding a
    new template to src/templates/ is enough to have it show up in output/, no
    separate list to update.
    """
    testing_name = Path(TESTING_TEMPLATE).name
    return [
        (path.name, f"templates/{path.name}")
        for path in sorted(TEMPLATES.iterdir())
        if path.is_file() and path.name != testing_name
    ]


def load_testcases():
    """Return [(name, html)] for every testcases/*.html, sorted by filename."""
    if not TESTCASES.is_dir():
        return []
    cases = []
    for path in sorted(TESTCASES.glob("*.html")):
        cases.append((path.stem, path.read_text(encoding="utf-8").rstrip("\n")))
    return cases


def load_sample_fields():
    if not SAMPLE_FIELDS.is_file():
        return {}
    return json.loads(SAMPLE_FIELDS.read_text(encoding="utf-8"))


def substitute_sample_fields(markup, fields):
    """Resolve Anki field placeholders for the test harness.

    Any field with no sample value is replaced by a visible marker rather than
    left as a literal {{...}}.
    """

    def replace(match):
        name = match.group(1)
        # {{Glossary}} is populated by the test harness at runtime instead
        if name == "Glossary":
            return ""
        if name in fields:
            return fields[name]
        return f'<span class="test-harness-missing-field">[{name}]</span>'

    return FIELD_RE.sub(replace, markup)


def build_test_harness(fields, testcases):
    """Build output/testing.html from templates."""

    # Anki expands {{FrontSide}} on the back of a card to the rendered front. The
    # test harness does the same, using each note type's own front + back template.
    note_type_blocks = []
    for type_name, front_template, back_template in NOTE_TYPES:
        front_markup = substitute_sample_fields(render(front_template), fields).strip("\n")

        back_markup = render(back_template)
        back_markup = back_markup.replace("{{FrontSide}}", front_markup)
        back_markup = substitute_sample_fields(back_markup, fields).strip("\n")

        for side, markup in (("front", front_markup), ("back", back_markup)):
            note_type_blocks.append(
                f'<template data-note-type="{type_name}" data-side="{side}">\n'
                f"{indent_block(markup, '    ')}\n"
                f"</template>"
            )

    testcase_blocks = [
        f'<template data-testcase="{name}">\n{indent_block(html, "    ")}\n</template>'
        for name, html in testcases
    ]

    replacements = {
        "note-types": "\n".join(note_type_blocks),
        "testcases": "\n\n".join(testcase_blocks),
    }

    out = []
    for line in render(TESTING_TEMPLATE).split("\n"):
        match = DIRECTIVE_RE.match(line)
        if match:
            indent, name = match.group(1), match.group(2)
            out.append(indent_block(replacements[name], indent))
        else:
            out.append(line)
    return "\n".join(out)


def build():
    """Return {output filename: contents}."""
    artifacts = {}

    for out_name, src_path in discover_templates():
        artifacts[out_name] = render(src_path) + "\n"

    fields = load_sample_fields()
    testcases = load_testcases()
    if not testcases:
        print("warning: no test cases found in testcases/*.html", file=sys.stderr)
    artifacts["testing.html"] = build_test_harness(fields, testcases).rstrip("\n") + "\n"

    return artifacts


def main():
    try:
        artifacts = build()
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for name, contents in sorted(artifacts.items()):
        (OUTPUT / name).write_text(contents, encoding="utf-8")
        print(f"wrote output/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
