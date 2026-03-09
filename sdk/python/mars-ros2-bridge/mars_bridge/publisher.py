"""MARSPublisher — serialises a MARS record to JSON and outputs it."""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO


class MARSPublisher:
    """Converts a MARS record dict to a validated JSON string and writes it.

    Parameters
    ----------
    stream:
        File-like object to write to.  Defaults to ``sys.stdout``.
    indent:
        JSON indentation level.  ``None`` produces compact single-line output.
    """

    def __init__(self, stream: TextIO | None = None, indent: int | None = 2) -> None:
        self._stream: TextIO = stream or sys.stdout
        self._indent = indent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def publish(self, record: dict[str, Any]) -> str:
        """Serialise *record* to JSON, write to the configured stream, and
        return the JSON string.

        Raises
        ------
        ValueError
            If *record* fails basic structural validation.
        """
        self._validate(record)
        payload = json.dumps(record, indent=self._indent, default=str)
        self._stream.write(payload)
        self._stream.write("\n")
        return payload

    def to_json(self, record: dict[str, Any]) -> str:
        """Return JSON string without writing to any stream."""
        self._validate(record)
        return json.dumps(record, indent=self._indent, default=str)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(record: dict[str, Any]) -> None:
        required = {"schema_version", "robot_id"}
        missing = required - record.keys()
        if missing:
            raise ValueError(
                f"MARS record is missing required top-level keys: {missing}"
            )
        if not record.get("robot_id"):
            raise ValueError("MARS record 'robot_id' must not be empty.")
