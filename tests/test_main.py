import py_compile
from pathlib import Path

import tomllib

import socialmedia

ROOT = Path(__file__).resolve().parents[1]


def test_version_is_defined():
    assert socialmedia.__version__


def test_plugin_entrypoint_uses_installable_module():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert (
        config["project"]["entry-points"]["pretix.plugin"]["socialmedia"]
        == "socialmedia"
    )


def test_app_config_module_compiles():
    py_compile.compile(str(ROOT / "socialmedia" / "apps.py"), doraise=True)
