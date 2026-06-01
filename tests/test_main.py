import py_compile
import tomllib
from pathlib import Path

import eventyay_socialmedia

ROOT = Path(__file__).resolve().parents[1]


def test_version_is_defined():
    assert eventyay_socialmedia.__version__


def test_plugin_entrypoint_uses_installable_module():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert (
        config["project"]["entry-points"]["pretix.plugin"]["eventyay_socialmedia"]
        == "eventyay_socialmedia"
    )


def test_app_config_module_compiles():
    py_compile.compile(str(ROOT / "eventyay_socialmedia" / "apps.py"), doraise=True)
