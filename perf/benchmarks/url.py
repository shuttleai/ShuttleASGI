"""
URL methods.
"""

from shuttleasgi.url import URL
from perf.benchmarks import main_run, sync_benchmark

ITERATIONS = 10000


def test_url_instantiate():
    url = URL(b"https://www.neoteroi.dev/shuttleasgi/?super=yes#some-hash")
    assert url.value == b"https://www.neoteroi.dev/shuttleasgi/?super=yes#some-hash"
    assert url.host == b"www.neoteroi.dev"
    assert url.port in {0, 443}
    assert url.path == b"/shuttleasgi/"
    assert url.query == b"super=yes"
    assert url.is_absolute is True
    assert url.schema == b"https"
    assert url.fragment == b"some-hash"


def benchmark_url_instantiate(iterations=ITERATIONS):
    return sync_benchmark(test_url_instantiate, iterations)


if __name__ == "__main__":
    main_run(benchmark_url_instantiate)
