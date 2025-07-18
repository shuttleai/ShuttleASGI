# cython: language_level=3

# This file declares the C-level functions that can be cimported and called
# efficiently by other Cython modules.

cdef void validate_chat_completion_fast(dict payload) except *

cpdef dict parse_and_validate_json(bytes json_data, str endpoint) except *