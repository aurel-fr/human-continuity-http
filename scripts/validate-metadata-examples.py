#!/usr/bin/env python3
"""Validate the draft's metadata examples against the informative JSON Schemas.

Every ``~~~ json`` block in the draft is classified explicitly. Policy metadata
and realm metadata documents are validated against the corresponding schema in
``schemas/``. Known non-metadata documents (verifier output, JWK Sets, and
Problem Details) are skipped and reported. An unrecognized block fails the
check, so adding a new metadata example cannot silently escape validation.

Exits non-zero if any example fails, if a block is unparseable, or if either
document type ends up with no examples at all.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError:
    sys.exit(
        "error: missing dependency 'jsonschema'\n"
        "  install it with: python3 -m pip install 'jsonschema[format]==4.26.0'"
    )

ROOT = Path(__file__).resolve().parent.parent
JSON_BLOCK = re.compile(r"~~~ json\r?\n(.*?)\r?\n~~~", re.DOTALL)

# Classification uses all required top-level keys as a structural signature. A
# score, ensures that omitting or misspelling a required member still routes the document to the schema that reports the
# error. Verifier output is checked first because it intentionally shares
# "realm" with realm metadata. Other non-metadata signatures are checked only
# when no metadata signature matches, so extension members cannot hide metadata.
SCHEMAS = (
    (
        "policy metadata",
        {"origin", "policies", "policy_selectors", "default_policy_selectors"},
        "human-continuity-policy-metadata.schema.json",
    ),
    (
        "realm metadata",
        {"realm", "profiles"},
        "human-continuity-realm-metadata.schema.json",
    ),
)

VERIFIER_OUTPUT_SIGNATURE = {
    "state",
    "profile",
    "realm",
    "policy_identifier",
    "attestation_audience",
    "purpose",
    "continuity_handle",
}

OTHER_NON_METADATA_SIGNATURES = (
    ("JWK Set", {"keys"}),
    ("Problem Details", {"type", "status"}),
)


class DuplicateMemberError(ValueError):
    """Raised when a JSON object repeats a member name."""


def reject_duplicate_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    document = {}
    for name, value in pairs:
        if name in document:
            raise DuplicateMemberError(f"duplicate member {name!r}")
        document[name] = value
    return document


def parse_json(source: str) -> object:
    return json.loads(source, object_pairs_hook=reject_duplicate_members)


def other_non_metadata_reason(document: dict[str, object]) -> str | None:
    keys = document.keys()
    return next(
        (
            label
            for label, signature in OTHER_NON_METADATA_SIGNATURES
            if signature <= keys
        ),
        None,
    )


def classify_document(document: dict[str, object]) -> str | None:
    best_label = None
    best_score = 0
    for label, signature, _ in SCHEMAS:
        score = len(signature & document.keys())
        if score > best_score:
            best_label = label
            best_score = score
    return best_label


def find_draft() -> Path:
    drafts = sorted(ROOT.glob("draft-*.md"))
    if len(drafts) != 1:
        sys.exit(
            f"error: expected exactly one draft-*.md in {ROOT}, found {len(drafts)}"
        )
    return drafts[0]


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main() -> int:
    draft = find_draft()
    source = draft.read_text()

    validators = {}
    format_checker = FormatChecker()
    for label, _, filename in SCHEMAS:
        path = ROOT / "schemas" / filename
        if not path.is_file():
            sys.exit(f"error: missing schema {path}")
        try:
            schema = parse_json(path.read_text())
        except (json.JSONDecodeError, DuplicateMemberError) as exc:
            sys.exit(f"error: invalid schema {path}: {exc}")
        Draft202012Validator.check_schema(schema)
        validators[label] = Draft202012Validator(
            schema,
            format_checker=format_checker,
        )

    failures = 0
    counts = {label: 0 for label, _, _ in SCHEMAS}
    skipped = []

    for match in JSON_BLOCK.finditer(source):
        line = line_of(source, match.start())
        where = f"{draft.name}:{line}"
        try:
            document = parse_json(match.group(1))
        except (json.JSONDecodeError, DuplicateMemberError) as exc:
            print(f"FAIL  {where}  invalid JSON document: {exc}")
            failures += 1
            continue

        if not isinstance(document, dict):
            print(f"FAIL  {where}  unrecognized JSON value (not an object)")
            failures += 1
            continue

        if VERIFIER_OUTPUT_SIGNATURE <= document.keys():
            skipped.append((where, "verifier output"))
            continue

        label = classify_document(document)
        if label is None:
            reason = other_non_metadata_reason(document)
            if reason is not None:
                skipped.append((where, reason))
                continue
            keys = "+".join(sorted(document.keys())[:4]) or "empty object"
            print(f"FAIL  {where}  unrecognized JSON object ({keys})")
            failures += 1
            continue

        counts[label] += 1
        errors = sorted(
            validators[label].iter_errors(document), key=lambda e: list(e.path)
        )
        if errors:
            failures += 1
            print(f"FAIL  {where}  {label}")
            for error in errors:
                location = "/".join(str(part) for part in error.path) or "(root)"
                print(f"        {location}: {error.message}")
        else:
            print(f"ok    {where}  {label}")

    for where, reason in skipped:
        print(f"skip  {where}  {reason}")

    for label, count in counts.items():
        if count == 0:
            print(f"FAIL  no {label} examples found in {draft.name}")
            failures += 1

    summary = ", ".join(f"{count} {label}" for label, count in counts.items())
    print(f"\n{summary}, {len(skipped)} skipped, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
