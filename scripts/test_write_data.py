import timeit

setup_code = """
from shuttleasgi.contents import TextServerSentEvent, DONEServerSentEvent
data = "[DONE]"
text_event = TextServerSentEvent(data)
done_event = DONEServerSentEvent()
"""

N = 1000000
R = 5

print(f"Running {R} trials of {N} iterations each...\n")

text_results = timeit.repeat(
    "text_event.write_data()",
    setup=setup_code,
    number=N,
    repeat=R
)
text_best_time = min(text_results)

print(f"All trials for Text event: {[f'{t:.4f}' for t in text_results]}")
print(f"Best time for Text event: {text_best_time:.4f} seconds")
print("-" * 30)

done_results = timeit.repeat(
    "done_event.write_data()",
    setup=setup_code,
    number=N,
    repeat=R
)
done_best_time = min(done_results)

print(f"All trials for DONE event: {[f'{t:.4f}' for t in done_results]}")
print(f"Best time for DONE event: {done_best_time:.4f} seconds")