import timeit
from collections import UserDict
from contextvars import ContextVar, copy_context

# ======= BlackSheep-style _Context using UserDict =======
_request_scope_context_storage_bs: ContextVar[dict] = ContextVar("blacksheep_context")

class _ContextBS(UserDict):
    def __init__(self, *args, **kwargs):
        # forbid init args to match blacksheep-context behavior
        if args or kwargs:
            raise RuntimeError("Can't instantiate with initial data")

    @property
    def data(self):
        try:
            return _request_scope_context_storage_bs.get()
        except LookupError:
            raise RuntimeError("Context does not exist")

    def exists(self) -> bool:
        return _request_scope_context_storage_bs in copy_context()

    def copy(self):
        return self.data.copy()

context_bs = _ContextBS()

# ======= ShuttleASGI-style minimal context =======
_request_scope_context_storage_sa: ContextVar[dict] = ContextVar("shuttle_context")

class RequestContextSA:
    def get(self):
        return _request_scope_context_storage_sa.get()

    def exists(self) -> bool:
        try:
            _request_scope_context_storage_sa.get()
            return True
        except LookupError:
            return False

    def copy(self):
        return self.get().copy()

context_sa = RequestContextSA()

# ======= Helpers to set/reset context =======
def set_bs_context(data):
    return _request_scope_context_storage_bs.set(data)

def reset_bs_context(token):
    _request_scope_context_storage_bs.reset(token)

def set_sa_context(data):
    return _request_scope_context_storage_sa.set(data)

def reset_sa_context(token):
    _request_scope_context_storage_sa.reset(token)

# ======= Benchmark runner =======
def run_benchmark():
    ITERATIONS = 100_000
    sample_data = {"req_id": "123", "user": "alice"}

    # Setup context for both
    token_bs = set_bs_context(sample_data)
    token_sa = set_sa_context(sample_data)

    # Benchmark exists()
    exists_bs_time = timeit.timeit(lambda: context_bs.exists(), number=ITERATIONS)
    exists_sa_time = timeit.timeit(lambda: context_sa.exists(), number=ITERATIONS)

    # Benchmark copy()
    copy_bs_time = timeit.timeit(lambda: context_bs.copy(), number=ITERATIONS)
    copy_sa_time = timeit.timeit(lambda: context_sa.copy(), number=ITERATIONS)

    # Reset context
    reset_bs_context(token_bs)
    reset_sa_context(token_sa)

    print("Benchmark results (100,000 iterations):")
    print(f"BlackSheep-style exists() time: {exists_bs_time:.5f} sec")
    print(f"ShuttleASGI-style exists() time: {exists_sa_time:.5f} sec")
    print(f"BlackSheep-style copy()   time: {copy_bs_time:.5f} sec")
    print(f"ShuttleASGI-style copy()  time: {copy_sa_time:.5f} sec")

    print("\nSpeedup:")
    print(f"exists() ShuttleASGI is {exists_bs_time / exists_sa_time:.2f}x faster than BlackSheep-style")
    print(f"copy()   ShuttleASGI is {copy_bs_time / copy_sa_time:.2f}x faster than BlackSheep-style")

if __name__ == "__main__":
    run_benchmark()
