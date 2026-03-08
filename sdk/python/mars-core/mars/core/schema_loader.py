"""
Loads the MARS v0.9 JSON Schema from package resources with caching.
"""

import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=1)
def load_schema() -> dict:
    """Load and cache the MARS v0.9 JSON schema from package resources.

    Returns the schema as a Python dict. Subsequent calls return the cached
    result with no file I/O.
    """
    schema_text = files("mars").joinpath("MARS_v0.9.json").read_text(encoding="utf-8")
    return json.loads(schema_text)
