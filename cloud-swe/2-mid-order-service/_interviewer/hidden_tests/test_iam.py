import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_iam import find_problems  # noqa: E402


def test_template_has_no_wildcard_permissions():
    assert find_problems(str(ROOT / "infra" / "template.yaml")) == []
