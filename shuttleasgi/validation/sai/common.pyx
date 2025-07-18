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


cdef class ValidationError(Exception):
    def __init__(self, str message, str error_type, str param, str code, str hint):
        self.message = message
        self.error_type = error_type
        self.param = param
        self.code = code
        self.hint = hint
        super().__init__(message)
