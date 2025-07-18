# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True
# cython: infer_types=True
# cython: optimize.use_switch=True
# cython: optimize.unpack_method_calls=True
# cython: profile=False

import cython
from cpython.dict cimport PyDict_GetItem
from cpython.list cimport PyList_GET_ITEM, PyList_GET_SIZE
from cpython.long cimport PyLong_AsLong, PyLong_AsLongLong
from cpython.float cimport PyFloat_AsDouble
from cpython.object cimport PyObject, PyTypeObject
from cpython.exc cimport PyErr_Occurred, PyErr_Clear
from .common import ValidationError
import orjson

# --- Interned Keys for Top-Level and Nested Properties ---
KEY_MODEL = intern("model")
KEY_MESSAGES = intern("messages")
KEY_MAX_COMPLETION_TOKENS = intern("max_completion_tokens")
KEY_FREQUENCY_PENALTY = intern("frequency_penalty")
KEY_PRESENCE_PENALTY = intern("presence_penalty")
KEY_RESPONSE_FORMAT = intern("response_format")
KEY_SEED = intern("seed")
KEY_STREAM = intern("stream")
KEY_STREAM_OPTIONS = intern("stream_options")
KEY_STOP = intern("stop")
KEY_TOOLS = intern("tools")
KEY_TOOL_CHOICE = intern("tool_choice")
KEY_PARALLEL_TOOL_CALLS = intern("parallel_tool_calls")
KEY_N = intern("n")
KEY_METADATA = intern("metadata")
KEY_TEMPERATURE = intern("temperature")
KEY_TOP_P = intern("top_p")
KEY_REASONING_EFFORT = intern("reasoning_effort")
KEY_WEB_SEARCH_OPTIONS = intern("web_search_options")

# --- Interned Keys for Message Structure ---
KEY_ROLE = intern("role")
KEY_CONTENT = intern("content")
KEY_NAME = intern("name")
KEY_REFUSAL = intern("refusal")
KEY_AUDIO = intern("audio")
KEY_ID = intern("id")
KEY_TOOL_CALLS = intern("tool_calls")
KEY_TOOL_CALL_ID = intern("tool_call_id")
KEY_TYPE = intern("type")
KEY_TEXT = intern("text")
KEY_IMAGE_URL = intern("image_url")
KEY_URL = intern("url")
KEY_DETAIL = intern("detail")
KEY_INPUT_AUDIO = intern("input_audio")
KEY_DATA = intern("data")
KEY_FORMAT = intern("format")
KEY_FILE = intern("file")
KEY_FILENAME = intern("filename")
KEY_FILE_DATA = intern("file_data")
KEY_FILE_ID = intern("file_id")

# --- Interned Keys for Tools and Functions ---
KEY_FUNCTION = intern("function")
KEY_ARGUMENTS = intern("arguments")
KEY_DESCRIPTION = intern("description")
KEY_PARAMETERS = intern("parameters")
KEY_STRICT = intern("strict")

# --- Interned Keys for Other Nested Objects ---
KEY_USER_LOCATION = intern("user_location")
KEY_APPROXIMATE = intern("approximate")
KEY_COUNTRY = intern("country")
KEY_REGION = intern("region")
KEY_CITY = intern("city")
KEY_TIMEZONE = intern("timezone")
KEY_SEARCH_CONTEXT_SIZE = intern("search_context_size")
KEY_JSON_SCHEMA = intern("json_schema")
KEY_SCHEMA = intern("schema")
KEY_INCLUDE_USAGE = intern("include_usage")

# --- Interned Enum Values ---
ROLE_SYSTEM = intern("system")
ROLE_USER = intern("user")
ROLE_ASSISTANT = intern("assistant")
ROLE_TOOL = intern("tool")
ROLE_DEVELOPER = intern("developer")

TYPE_TEXT = intern("text")
TYPE_JSON_OBJECT = intern("json_object")
TYPE_JSON_SCHEMA = intern("json_schema")
TYPE_FUNCTION = intern("function")
TYPE_IMAGE_URL = intern("image_url")
TYPE_INPUT_AUDIO = intern("input_audio")
TYPE_FILE = intern("file")
TYPE_REFUSAL = intern("refusal")
TYPE_APPROXIMATE_ENUM = intern("approximate")

TOOL_CHOICE_NONE = intern("none")
TOOL_CHOICE_AUTO = intern("auto")
TOOL_CHOICE_REQUIRED = intern("required")


# --- C-level Type Pointers for ultra-fast type checks ---
cdef PyTypeObject* IntType = <PyTypeObject*>int
cdef PyTypeObject* FloatType = <PyTypeObject*>float
cdef PyTypeObject* StrType = <PyTypeObject*>str
cdef PyTypeObject* BoolType = <PyTypeObject*>bool
cdef PyTypeObject* DictType = <PyTypeObject*>dict
cdef PyTypeObject* ListType = <PyTypeObject*>list


# --- Validation Helper Functions ---
# (we make multiple for performance/speed purposes)
cdef inline void _raise_error(str message, str path) except *:
    # A simple wrapper for consistent error raising
    raise ValidationError(message, "invalid_request_error", path, None)

cdef inline void _raise_error_with_code(str message, str path, str code) except *:
    raise ValidationError(message, "invalid_request_error", path, code)

# TODO: use bottom 2 (add hints)
cdef inline void _raise_error_with_hint(str message, str path, str hint) except *:
    raise ValidationError(message, "invalid_request_error", path, None, hint)

cdef inline void _raise_error_with_code_and_hint(str message, str path, str code, str hint) except *:
    raise ValidationError(message, "invalid_request_error", path, code, hint)

cdef inline void _validate_int(dict payload, object key, str path, long min_val, long max_val) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, key)
    cdef object value
    cdef long int_val
    if obj_ptr != NULL:
        value = <object>obj_ptr
        if value is not None:
            if (<PyObject*>value).ob_type is not IntType or (<PyObject*>value).ob_type is BoolType:
                _raise_error(f"must be an integer, but got {type(value).__name__}", path)
            int_val = PyLong_AsLong(value)
            if int_val == -1 and PyErr_Occurred() != NULL:
                PyErr_Clear()
                _raise_error(f"integer value out of range", path)
            if int_val < min_val:
                _raise_error(f"must be at least {min_val}", path)
            if int_val > max_val:
                _raise_error(f"must not exceed {max_val}", path)

cdef inline void _validate_long_long(dict payload, object key, str path, long long min_val, long long max_val) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, key)
    cdef object value
    cdef long long long_val
    if obj_ptr != NULL:
        value = <object>obj_ptr
        if value is not None:
            if (<PyObject*>value).ob_type is not IntType or (<PyObject*>value).ob_type is BoolType:
                _raise_error(f"must be an integer, but got {type(value).__name__}", path)
            long_val = PyLong_AsLongLong(value)
            if long_val == -1 and PyErr_Occurred() != NULL:
                PyErr_Clear()
                _raise_error(f"integer value out of range", path)
            if long_val < min_val:
                _raise_error(f"must be at least {min_val}", path)
            if long_val > max_val:
                _raise_error(f"must not exceed {max_val}", path)

cdef inline void _validate_number(dict payload, object key, str path, double min_val, double max_val) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, key)
    cdef object value
    cdef double num_val
    cdef PyTypeObject* value_type
    if obj_ptr != NULL:
        value = <object>obj_ptr
        if value is not None:
            value_type = (<PyObject*>value).ob_type
            if value_type is FloatType:
                num_val = PyFloat_AsDouble(value)
            elif value_type is IntType and value_type is not BoolType:
                num_val = <double>PyLong_AsLong(value)
            else:
                _raise_error(f"must be a number, but got {type(value).__name__}", path)
            if num_val < min_val:
                _raise_error(f"must be at least {min_val}", path)
            if num_val > max_val:
                _raise_error(f"must not exceed {max_val}", path)

cdef inline void _validate_string(dict payload, object key, str path, bint nullable=False) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, key)
    if obj_ptr == NULL: return
    cdef object value = <object>obj_ptr
    if value is None:
        if not nullable: _raise_error("must be a string, but got null", path)
    elif (<PyObject*>value).ob_type is not StrType:
        _raise_error(f"must be a string, but got {type(value).__name__}", path)

cdef inline void _validate_bool(dict payload, object key, str path, bint nullable=False) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, key)
    if obj_ptr == NULL: return
    cdef object value = <object>obj_ptr
    if value is None:
        if not nullable: _raise_error("must be a boolean, but got null", path)
    elif (<PyObject*>value).ob_type is not BoolType:
        _raise_error(f"must be a boolean, but got {type(value).__name__}", path)

cdef inline void _validate_metadata(dict payload) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, KEY_METADATA)
    if obj_ptr == NULL: return
    cdef object value = <object>obj_ptr
    if value is None: return

    if (<PyObject*>value).ob_type is not DictType:
        _raise_error("must be an object or null", "metadata")
    if len(value) > 16:
        _raise_error("can contain at most 16 key-value pairs", "metadata")
    for k, v in value.items():
        if (<PyObject*>k).ob_type is not StrType or (<PyObject*>v).ob_type is not StrType:
            _raise_error("all keys and values must be strings", "metadata")

cdef inline void _validate_stop(dict payload) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, KEY_STOP)
    if obj_ptr == NULL: return
    cdef object value = <object>obj_ptr
    cdef PyTypeObject* value_type = (<PyObject*>value).ob_type

    if value is None: return

    if value_type is StrType:
        return # Valid
    elif value_type is ListType:
        if len(value) < 1:
            _raise_error("must contain at least 1 item", "stop")
        if len(value) > 4:
            _raise_error("must contain at most 4 items", "stop")
        for i, item in enumerate(value):
            if (<PyObject*>item).ob_type is not StrType:
                _raise_error(f"item at index {i} must be a string", f"stop[{i}]")
    else:
        _raise_error("must be a string, an array of strings, or null", "stop")

# --- Content Part Validators ---

cdef inline void _validate_content_part_image(dict part, str path) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(part, KEY_IMAGE_URL)
    cdef object image_url
    if obj_ptr == NULL: _raise_error(f"Missing required parameter: {path}.image_url", f"{path}.image_url")
    image_url = <object>obj_ptr
    if (<PyObject*>image_url).ob_type is not DictType: _raise_error("must be an object", f"{path}.image_url")
    if PyDict_GetItem(image_url, KEY_URL) == NULL: _raise_error(f"Missing required parameter: {path}.image_url.url", f"{path}.image_url.url")
    _validate_string(image_url, KEY_URL, f"{path}.image_url.url")
    # A full URI validation is slow, we'll trust the string type for speed.

cdef inline void _validate_content_part(dict part, str path, set valid_types) except *:
    cdef PyObject* type_ptr = PyDict_GetItem(part, KEY_TYPE)
    cdef object part_type

    if type_ptr == NULL:
        _raise_error(f"Missing required parameter: '{path}.type", f"{path}.type")
        return # Unreachable, but good practice

    part_type = intern(<object>type_ptr)
    if part_type not in valid_types:
        _raise_error(f"type must be one of {valid_types}", f"{path}.type")

    if part_type is TYPE_TEXT:
        if PyDict_GetItem(part, KEY_TEXT) == NULL: _raise_error("is required for type 'text'", f"{path}.text")
        _validate_string(part, KEY_TEXT, f"{path}.text")
    elif part_type is TYPE_IMAGE_URL:
        _validate_content_part_image(part, path)
    # Add other content part validations (audio, file, etc.) here if needed, following the same pattern.

# --- Message Validators ---

cdef inline void _validate_message_content(dict message, str path_prefix, set valid_content_part_types, bint nullable=False) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(message, KEY_CONTENT)
    if obj_ptr == NULL:
        if not nullable: _raise_error("is required", f"{path_prefix}.content")
        return
    cdef object content = <object>obj_ptr
    cdef PyTypeObject* content_type = (<PyObject*>content).ob_type
    if content is None:
        if not nullable: _raise_error("cannot be null for this role", f"{path_prefix}.content")
        return

    if content_type is StrType:
        return # Valid
    elif content_type is ListType:
        if len(content) < 1:
            _raise_error("must contain at least one part", f"{path_prefix}.content")
        for i, part in enumerate(content):
            if (<PyObject*>part).ob_type is not DictType:
                _raise_error(f"part at index {i} must be an object", f"{path_prefix}.content[{i}]")
            _validate_content_part(part, f"{path_prefix}.content[{i}]", valid_content_part_types)
    else:
        _raise_error("must be a string or an array of content parts", f"{path_prefix}.content")

cdef inline void _validate_message_item(dict message, int index) except *:
    cdef str path_prefix = f"messages[{index}]"
    if (<PyObject*>message).ob_type is not DictType:
        _raise_error(f"item at index {index} must be an object", "messages")

    cdef PyObject* role_ptr = PyDict_GetItem(message, KEY_ROLE)
    if role_ptr == NULL: _raise_error("is required", f"{path_prefix}.role")

    cdef object role = intern(<object>role_ptr)
    
    _validate_string(message, KEY_NAME, f"{path_prefix}.name", nullable=True)

    if role is ROLE_SYSTEM:
        _validate_message_content(message, path_prefix, {TYPE_TEXT})
    elif role is ROLE_USER:
        _validate_message_content(message, path_prefix, {TYPE_TEXT, TYPE_IMAGE_URL, TYPE_INPUT_AUDIO, TYPE_FILE})
    elif role is ROLE_ASSISTANT:
        _validate_message_content(message, path_prefix, {TYPE_TEXT, TYPE_REFUSAL}, nullable=True)
        # TODO: Add validation for tool_calls if necessary
    elif role is ROLE_TOOL:
        if PyDict_GetItem(message, KEY_TOOL_CALL_ID) == NULL:
            _raise_error("is required for role 'tool'", f"{path_prefix}.tool_call_id")
        _validate_string(message, KEY_TOOL_CALL_ID, f"{path_prefix}.tool_call_id")
        _validate_message_content(message, path_prefix, {TYPE_TEXT})
    elif role is ROLE_DEVELOPER:
        _validate_message_content(message, path_prefix, {TYPE_TEXT})
    else:
        _raise_error_with_code(f"Invalid value: '{<object>role_ptr}'. Supported values are: 'system', 'assistant', 'user', 'function', 'tool', and 'developer'.", f"{path_prefix}.role", "invalid_value")

cdef inline void _validate_messages(dict payload) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, KEY_MESSAGES)
    if obj_ptr == NULL: _raise_error_with_code(f"Missing required parameter: 'messages'", "messages", "missing_required_parameter")
    cdef object messages = <object>obj_ptr
    if (<PyObject*>messages).ob_type is not ListType: _raise_error("must be an array", "messages")
    
    cdef Py_ssize_t length = PyList_GET_SIZE(messages)
    if length < 1: _raise_error("must contain at least 1 message", "messages")

    for i in range(length):
        _validate_message_item(<dict>PyList_GET_ITEM(messages, i), i)

# --- Tool and Function Validators ---

cdef inline void _validate_function_object(dict func, str path) except *:
    if PyDict_GetItem(func, KEY_NAME) == NULL: _raise_error("is required", f"{path}.name")
    _validate_string(func, KEY_NAME, f"{path}.name")
    _validate_string(func, KEY_DESCRIPTION, f"{path}.description", nullable=True)
    _validate_bool(func, KEY_STRICT, f"{path}.strict", nullable=True)
    cdef PyObject* params_ptr = PyDict_GetItem(func, KEY_PARAMETERS)
    if params_ptr != NULL and (<PyObject*><object>params_ptr).ob_type is not DictType:
        _raise_error("must be an object", f"{path}.parameters")

cdef inline void _validate_tool(dict tool, int index) except *:
    cdef str path = f"tools[{index}]"
    cdef PyObject* type_ptr = NULL
    cdef PyObject* func_ptr = NULL
    cdef object func = None
    
    if (<PyObject*>tool).ob_type is not DictType: _raise_error("must be an object", path)

    type_ptr = PyDict_GetItem(tool, KEY_TYPE)
    if type_ptr == NULL or intern(<object>type_ptr) is not TYPE_FUNCTION:
        _raise_error("type must be 'function'", f"{path}.type")

    func_ptr = PyDict_GetItem(tool, KEY_FUNCTION)
    if func_ptr == NULL: _raise_error("is required", f"{path}.function")
    func = <object>func_ptr
    if (<PyObject*>func).ob_type is not DictType: _raise_error("must be an object", f"{path}.function")
    _validate_function_object(func, f"{path}.function")

cdef inline void _validate_tools(dict payload) except *:
    cdef PyObject* obj_ptr = PyDict_GetItem(payload, KEY_TOOLS)
    if obj_ptr == NULL: return
    cdef object tools = <object>obj_ptr
    if (<PyObject*>tools).ob_type is not ListType: _raise_error("must be an array", "tools")

    for i in range(PyList_GET_SIZE(tools)):
        _validate_tool(<dict>PyList_GET_ITEM(tools, i), i)
        
# --- Complex Field Validators ---

cdef inline void _validate_tool_choice(dict payload) except *:
    cdef PyObject* obj_ptr = NULL
    cdef PyObject* func_ptr = NULL
    cdef PyObject* type_ptr = NULL
    cdef object choice = None
    cdef object func = None
    cdef object interned_choice = None
    cdef PyTypeObject* choice_type

    obj_ptr = PyDict_GetItem(payload, KEY_TOOL_CHOICE)
    if obj_ptr == NULL: return
    choice = <object>obj_ptr
    choice_type = (<PyObject*>choice).ob_type

    if choice_type is StrType:
        interned_choice = intern(choice)
        if not (interned_choice is TOOL_CHOICE_NONE or interned_choice is TOOL_CHOICE_AUTO or interned_choice is TOOL_CHOICE_REQUIRED):
            _raise_error("must be one of 'none', 'auto', 'required', or a tool choice object", "tool_choice")
    elif choice_type is DictType:
        type_ptr = PyDict_GetItem(choice, KEY_TYPE)
        if type_ptr == NULL or intern(<object>type_ptr) is not TYPE_FUNCTION:
            _raise_error("type must be 'function'", "tool_choice.type")

        func_ptr = PyDict_GetItem(choice, KEY_FUNCTION)
        if func_ptr == NULL: _raise_error("is required", "tool_choice.function")

        func = <object>func_ptr
        if (<PyObject*>func).ob_type is not DictType: _raise_error("must be an object", "tool_choice.function")
        if PyDict_GetItem(func, KEY_NAME) == NULL: _raise_error("is required", "tool_choice.function.name")
        _validate_string(func, KEY_NAME, "tool_choice.function.name")
    else:
        _raise_error("must be a string or an object", "tool_choice")

cdef inline void _validate_response_format(dict payload) except *:
    cdef PyObject* obj_ptr = NULL
    cdef PyObject* schema_ptr = NULL
    cdef PyObject* inner_schema_ptr = NULL
    cdef PyObject* type_ptr = NULL
    cdef object rformat = None
    cdef object rtype = None
    cdef object schema_obj = None

    obj_ptr = PyDict_GetItem(payload, KEY_RESPONSE_FORMAT)
    if obj_ptr == NULL: return
    rformat = <object>obj_ptr
    if (<PyObject*>rformat).ob_type is not DictType: _raise_error("must be an object", "response_format")

    type_ptr = PyDict_GetItem(rformat, KEY_TYPE)
    if type_ptr == NULL:
        _raise_error("is required", "response_format.type")
        return # Unreachable
    
    rtype = intern(<object>type_ptr)

    if rtype is TYPE_TEXT or rtype is TYPE_JSON_OBJECT:
        return # No other properties to validate
    elif rtype is TYPE_JSON_SCHEMA:
        schema_ptr = PyDict_GetItem(rformat, KEY_JSON_SCHEMA)
        if schema_ptr == NULL: _raise_error("is required for type 'json_schema'", "response_format.json_schema")
        
        schema_obj = <object>schema_ptr
        if (<PyObject*>schema_obj).ob_type is not DictType: _raise_error("must be an object", "response_format.json_schema")
        if PyDict_GetItem(schema_obj, KEY_NAME) == NULL: _raise_error("is required", "response_format.json_schema.name")
        
        _validate_string(schema_obj, KEY_NAME, "response_format.json_schema.name")
        _validate_string(schema_obj, KEY_DESCRIPTION, "response_format.json_schema.description", nullable=True)
        _validate_bool(schema_obj, KEY_STRICT, "response_format.json_schema.strict", nullable=True)

        inner_schema_ptr = PyDict_GetItem(schema_obj, KEY_SCHEMA)
        if inner_schema_ptr != NULL and (<PyObject*><object>inner_schema_ptr).ob_type is not DictType:
             _raise_error("must be an object", "response_format.json_schema.schema")
    else:
        _raise_error("type must be one of 'text', 'json_object', 'json_schema'", "response_format.type")

# --- Main Validator ---

cdef void validate_chat_completion_fast(dict payload) except *:
    """Ultra-fast, single-pass, full-schema validation for CreateChatCompletionRequest."""
    
    # --- Required Fields ---
    if PyDict_GetItem(payload, KEY_MODEL) == NULL:
        _raise_error("you must provide a model parameter", "model")
    _validate_string(payload, KEY_MODEL, "model")
    
    _validate_messages(payload) # Handles its own required check

    # --- Optional Fields (from CreateChatCompletionRequest) ---
    _validate_int(payload, KEY_MAX_COMPLETION_TOKENS, "max_completion_tokens", 1, 4096)
    _validate_number(payload, KEY_FREQUENCY_PENALTY, "frequency_penalty", -2.0, 2.0)
    _validate_number(payload, KEY_PRESENCE_PENALTY, "presence_penalty", -2.0, 2.0)
    _validate_response_format(payload)
    _validate_long_long(payload, KEY_SEED, "seed", -9223372036854776000, 9223372036854776000)
    _validate_bool(payload, KEY_STREAM, "stream", nullable=True)
    _validate_stop(payload)
    _validate_int(payload, KEY_N, "n", 1, 128)
    _validate_tools(payload)
    _validate_tool_choice(payload)
    _validate_bool(payload, KEY_PARALLEL_TOOL_CALLS, "parallel_tool_calls", nullable=True)
    # TODO: Add validation for stream_options, web_search_options if needed

    # --- Optional Fields (from CreateModelResponseProperties) ---
    _validate_metadata(payload)
    _validate_number(payload, KEY_TEMPERATURE, "temperature", 0.0, 2.0)
    _validate_number(payload, KEY_TOP_P, "top_p", 0.0, 1.0)
    # TODO: Add validation for reasoning_effort if needed

# TODO: Move and expand (add endpoints)
cpdef dict parse_and_validate_json(bytes json_data, str endpoint):
    """Ultra-fast JSON parsing and validation with orjson"""
    cdef dict payload
    
    try:
        payload = orjson.loads(json_data)
    except orjson.JSONDecodeError:
        raise ValidationError("We could not parse the JSON body of your request. (HINT: This likely means you aren't using your HTTP library correctly. The ShuttleAI API expects a JSON payload, but what was sent was not valid JSON. If you have trouble figuring out how to fix this, please contact us through our discord support center at discord.shuttleai.com.)", "invalid_request_error", None, None)
    
    if (<PyObject*>payload).ob_type is not DictType:
        raise ValidationError("Request body must be an object", "invalid_request_error", None, None)
    
    # Endpoint routing allows for easy expansion to other request types
    if endpoint == "chat_completion":
        validate_chat_completion_fast(payload)
    else:
        raise NotImplementedError(f"Validation for endpoint '{endpoint}' is not implemented.")
    
    return payload