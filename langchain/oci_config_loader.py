"""
Utilities for loading local OCI configuration that we do not want in version control.

Create an `oci_config.py` file next to this module (ignored via `.gitignore`)
with a `COMPARTMENT_ID` constant that contains your compartment OCID, e.g.

```python
COMPARTMENT_ID = "ocid1.compartment....."
```
"""

from functools import lru_cache
from importlib import import_module


@lru_cache(maxsize=1)
def _load_config():
    try:
        return import_module("oci_config")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing OCI config. Copy `oci_config_template.py` to `oci_config.py` "
            "and fill in your OCI values."
        ) from exc


def get_compartment_id() -> str:
    """Load the compartment OCID from `oci_config.py` and validate it."""
    config = _load_config()
    compartment_id = getattr(config, "COMPARTMENT_ID", "").strip()
    if not compartment_id or compartment_id.startswith("ocid1.compartment.oc1..example"):
        raise ValueError(
            "Invalid `COMPARTMENT_ID` value. Update `oci_config.py` with your real compartment OCID."
        )
    return compartment_id


def get_service_endpoint() -> str:
    """Load the service endpoint from `oci_config.py` and validate it."""
    config = _load_config()
    service_endpoint = getattr(config, "SERVICE_ENDPOINT", "").strip()
    if not service_endpoint or service_endpoint.startswith("https://inference.generativeai.example.com"):
        raise ValueError(
            "Invalid `SERVICE_ENDPOINT` value. Update `oci_config.py` with your Generative AI endpoint URL."
        )
    return service_endpoint
