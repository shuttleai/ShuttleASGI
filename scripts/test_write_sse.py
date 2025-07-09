import time
from shuttleasgi.contents import TextServerSentEvent, DONEServerSentEvent, ServerSentEvent
from shuttleasgi.scribe import write_sse


def warmup():
    for _ in range(1000000):
        TextServerSentEvent("Warmup data")
        DONEServerSentEvent()

warmup()

data = "[DONE]"
event = TextServerSentEvent(data)
event2 = DONEServerSentEvent()
event3 = ServerSentEvent({
    "message": {
        "content": "This is a test message",
        "role": "assistant"
    }
})

start_time = time.perf_counter()
for _ in range(1000000):
    write_sse(event)
    write_sse(event2)
    write_sse(event3)
end_time = time.perf_counter()

print(f"Time taken for TextServerSentEvent.write_data(): {end_time - start_time:.6f} seconds")

#OG: Time taken for TextServerSentEvent.write_data(): 0.4698472023010254 seconds
#Opt 1: Time taken for TextServerSentEvent.write_data(): 0.22771859169006348 seconds
#Optimized 1: Time taken for TextServerSentEvent.write_data(): 0.1731257438659668 seconds
#Optimized 2: Time taken for TextServerSentEvent.write_data(): 0.14759349822998047 seconds


