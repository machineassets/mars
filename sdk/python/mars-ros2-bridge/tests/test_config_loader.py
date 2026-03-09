"""Tests for mars_bridge.config_loader."""

import os
import textwrap

import pytest

from mars_bridge.config_loader import ConfigLoader, ConfigValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestConfigLoaderHappyPath:
    def test_loads_mir200_config(self):
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "mir200_mapping.yaml"
        )
        loader = ConfigLoader(config_path)
        cfg = loader.load()

        assert cfg["robot_id"] == "mir200-001"
        assert cfg["mars_version"] == "0.9"
        assert isinstance(cfg["mappings"], list)
        assert len(cfg["mappings"]) > 0

    def test_loads_generic_config(self):
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "generic_mapping.yaml"
        )
        loader = ConfigLoader(config_path)
        cfg = loader.load()

        assert "robot_id" in cfg
        assert "mappings" in cfg

    def test_config_property_after_load(self, tmp_path):
        path = _write_yaml(tmp_path, "cfg.yaml", """
            robot_id: test-bot
            mars_version: "0.9"
            mappings:
              - topic: /test/topic
                source_field: value
                mars_field: operational_metrics.autonomy_score
        """)
        loader = ConfigLoader(path)
        loader.load()
        assert loader.config["robot_id"] == "test-bot"

    def test_each_mapping_has_required_keys(self):
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "mir200_mapping.yaml"
        )
        loader = ConfigLoader(config_path)
        cfg = loader.load()

        for entry in cfg["mappings"]:
            assert "topic" in entry
            assert "mars_field" in entry


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

class TestConfigLoaderErrors:
    def test_raises_file_not_found(self, tmp_path):
        loader = ConfigLoader(str(tmp_path / "nonexistent.yaml"))
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_raises_on_missing_top_key(self, tmp_path):
        path = _write_yaml(tmp_path, "bad.yaml", """
            robot_id: test-bot
            mappings:
              - topic: /x
                mars_field: operational_metrics.autonomy_score
        """)
        # missing mars_version
        loader = ConfigLoader(path)
        with pytest.raises(ConfigValidationError, match="mars_version"):
            loader.load()

    def test_raises_on_empty_mappings(self, tmp_path):
        path = _write_yaml(tmp_path, "empty.yaml", """
            robot_id: test-bot
            mars_version: "0.9"
            mappings: []
        """)
        loader = ConfigLoader(path)
        with pytest.raises(ConfigValidationError, match="non-empty"):
            loader.load()

    def test_raises_on_mapping_missing_mars_field(self, tmp_path):
        path = _write_yaml(tmp_path, "bad_entry.yaml", """
            robot_id: test-bot
            mars_version: "0.9"
            mappings:
              - topic: /test/topic
                source_field: value
        """)
        loader = ConfigLoader(path)
        with pytest.raises(ConfigValidationError, match="mars_field"):
            loader.load()

    def test_raises_on_mapping_missing_topic(self, tmp_path):
        path = _write_yaml(tmp_path, "no_topic.yaml", """
            robot_id: test-bot
            mars_version: "0.9"
            mappings:
              - mars_field: operational_metrics.autonomy_score
        """)
        loader = ConfigLoader(path)
        with pytest.raises(ConfigValidationError, match="topic"):
            loader.load()

    def test_config_property_before_load_raises(self, tmp_path):
        loader = ConfigLoader(str(tmp_path / "any.yaml"))
        with pytest.raises(RuntimeError):
            _ = loader.config
