"""Flags wildcard IAM actions and resources in a SAM/CloudFormation template.

Usage: python scripts/check_iam.py infra/template.yaml
Exits 1 if any statement grants "*" or "service:*" actions, or uses "*" as a resource.
"""
from __future__ import annotations

import sys

import yaml


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _statements(node):
    if isinstance(node, dict):
        if "Effect" in node and ("Action" in node or "Resource" in node):
            yield node
        for value in node.values():
            yield from _statements(value)
    elif isinstance(node, list):
        for item in node:
            yield from _statements(item)


def find_problems(path: str) -> list[str]:
    with open(path) as handle:
        template = yaml.safe_load(handle)
    problems = []
    for statement in _statements(template):
        if statement.get("Effect") != "Allow":
            continue
        for action in _as_list(statement.get("Action")):
            if isinstance(action, str) and (action == "*" or action.endswith(":*")):
                problems.append(f"wildcard action: {action}")
        for resource in _as_list(statement.get("Resource")):
            if resource == "*":
                problems.append('wildcard resource: "*"')
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_iam.py <template.yaml>", file=sys.stderr)
        return 2
    problems = find_problems(argv[1])
    for problem in problems:
        print(f"FAIL {problem}")
    if not problems:
        print("OK: no wildcard actions or resources")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
