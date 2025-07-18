# This stub file is for static type checking and IDE support.
# It only exposes the Python-accessible parts of the module.

from typing import Any, Dict
from .common import ValidationError

def parse_and_validate_json(json_data: bytes, endpoint: str) -> Dict[str, Any]:
    """
    Ultra-fast JSON parsing and validation with orjson.

    Args:
        json_data: The raw JSON body as bytes.
        endpoint: The name of the endpoint to validate against (e.g., "chat_completion").

    Returns:
        The parsed and validated payload as a Python dictionary.

    Raises:
        ValidationError: If the JSON is malformed or fails schema validation.
        NotImplementedError: If validation for the given endpoint is not implemented.
    """
    ...