"""Loads and validates YAML mapping configurations for the MARS bridge."""

from __future__ import annotations

import os
from typing import Any

import yaml


REQUIRED_TOP_KEYS = {"robot_id", "mars_version", "mappings"}
REQUIRED_MAPPING_KEYS = {"topic", "mars_field"}


class ConfigValidationError(ValueError):
    """Raised when a config file fails structural validation."""


class ConfigLoader:
    """Loads a YAML config file and validates its structure."""

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self._config: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> dict[str, Any]:
        """Parse the YAML file and validate it. Returns the config dict."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)

        if not isinstance(raw, dict):
            raise ConfigValidationError("Config root must be a YAML mapping.")

        self._validate(raw)
        self._config = raw
        return raw

    @property
    def config(self) -> dict[str, Any]:
        if self._config is None:
            raise RuntimeError("Config not loaded yet. Call load() first.")
        return self._config

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate(self, cfg: dict[str, Any]) -> None:
        missing = REQUIRED_TOP_KEYS - cfg.keys()
        if missing:
            raise ConfigValidationError(
                f"Config missing required top-level keys: {missing}"
            )

        if not isinstance(cfg["mappings"], list) or len(cfg["mappings"]) == 0:
            raise ConfigValidationError(
                "'mappings' must be a non-empty list of mapping entries."
            )

        for i, entry in enumerate(cfg["mappings"]):
            if not isinstance(entry, dict):
                raise ConfigValidationError(
                    f"Mapping entry {i} must be a YAML mapping, got {type(entry)}."
                )
            missing_keys = REQUIRED_MAPPING_KEYS - entry.keys()
            if missing_keys:
                raise ConfigValidationError(
                    f"Mapping entry {i} is missing required keys: {missing_keys}"
                )
