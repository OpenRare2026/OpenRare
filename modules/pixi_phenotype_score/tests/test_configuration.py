from __future__ import annotations

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from path_config import display_path, load_paths  # noqa: E402


class ConfigurationTests(unittest.TestCase):
    def test_example_config_has_only_relative_paths(self) -> None:
        config = PROJECT_ROOT / "config" / "paths.example.toml"
        with config.open("rb") as handle:
            values = tomllib.load(handle)["paths"]
        for name, value in values.items():
            self.assertFalse(Path(value).is_absolute(), name)

    def test_example_config_loads(self) -> None:
        settings = load_paths(PROJECT_ROOT / "config" / "paths.example.toml")
        self.assertEqual(settings.runtime_root, PROJECT_ROOT / "runtime")
        self.assertEqual(settings.hgnc_symbols.name, "hgnc_complete_set.txt")
        self.assertEqual(display_path(settings.hgnc_symbols), "external_data/hgnc/hgnc_complete_set.txt")

    def test_absolute_config_values_are_rejected(self) -> None:
        source = (PROJECT_ROOT / "config" / "paths.example.toml").read_text()
        absolute_runtime = "/" + "tmp" + "/" + "runtime"
        source = source.replace('runtime_root = "runtime"', f'runtime_root = "{absolute_runtime}"')
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "paths.toml"
            config.write_text(source)
            with self.assertRaisesRegex(ValueError, "must be relative"):
                load_paths(config)

    def test_source_has_no_server_path_literal(self) -> None:
        server_root = "/" + "mnt" + "/" + "workspace"
        server_address = ".".join(["172", "27", "206", "112"])
        for source in (PROJECT_ROOT / "src").glob("*.py"):
            text = source.read_text()
            self.assertNotIn(server_root, text, source.name)
            self.assertNotIn(server_address, text, source.name)


if __name__ == "__main__":
    unittest.main()
