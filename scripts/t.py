import struct
from datetime import datetime, timezone

def decode_request_id_time(request_id: bytes) -> datetime:
    """
    Decode a request ID and return the timestamp when it was created.
    
    Args:
        request_id: The request ID bytes (format: b'req_' + 32 hex chars)
        
    Returns:
        datetime: UTC timestamp when the request ID was generated
        
    Raises:
        ValueError: If the request ID format is invalid
    """
    if len(request_id) != 36 or not request_id.startswith(b'req_'):
        raise ValueError("Invalid request ID format")
    
    # Extract hex portion (skip 'req_' prefix)
    hex_str = request_id[4:].decode('ascii')
    
    # Convert hex string back to bytes
    try:
        uuid_bytes = bytes.fromhex(hex_str)
    except ValueError:
        raise ValueError("Invalid hex encoding in request ID")
    
    if len(uuid_bytes) != 16:
        raise ValueError("Invalid UUID length")
    
    # UUID7 format: timestamp (48 bits) + version/variant + random
    # Extract first 6 bytes for timestamp (48 bits)
    timestamp_bytes = uuid_bytes[:6]
    
    # Convert to milliseconds since Unix epoch
    timestamp_ms = struct.unpack('>Q', b'\x00\x00' + timestamp_bytes)[0]
    
    # Convert to datetime
    timestamp_s = timestamp_ms / 1000.0
    return datetime.fromtimestamp(timestamp_s, tz=timezone.utc)


def get_request_age_ms(request_id: bytes) -> float:
    """
    Get the age of a request in milliseconds.
    
    Args:
        request_id: The request ID bytes
        
    Returns:
        float: Age in milliseconds since the request ID was created
    """
    created_time = decode_request_id_time(request_id)
    now = datetime.now(timezone.utc)
    age_delta = now - created_time
    return age_delta.total_seconds() * 1000.0


# Example usage:
if __name__ == "__main__":
    # Simulate a request ID (you'd get this from your middleware)
    import uuid_utils as uuid
    
    # Create a test UUID7
    test_uuid = uuid.uuid7()
    test_bytes = test_uuid.bytes
    
    # Format it like your middleware does
    hex_str = ''.join(f'{b:02x}' for b in test_bytes)
    hex_str = "0197c7f522027050a39de23c0f00e0f7"
    request_id = b'req_' + hex_str.encode('ascii')
    
    print(f"Request ID: {request_id}")
    print(f"Created at: {decode_request_id_time(request_id)}")
    print(f"Age: {get_request_age_ms(request_id):.2f} ms")