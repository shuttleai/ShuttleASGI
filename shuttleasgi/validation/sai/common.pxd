# cython: language_level=3


cdef class ValidationError(Exception):
    cdef readonly str message
    cdef readonly str error_type
    cdef readonly str param
    cdef readonly str code
    cdef readonly str hint
