class ValidationError(Exception):
    """
    ShuttleAI Validation Error

    params:
        - message
        - error_type
        - param
        - code
        - hint
    """
    ...