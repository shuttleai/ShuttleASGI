import timeit
import uuid_utils as uuid
import secrets

def uuid4_id():
    return uuid.uuid4().hex

def secrets_id():
    return secrets.token_hex(16)

# warm up
for _ in range(1000):
    uuid4_id()
    secrets_id()

print("uuid4:", timeit.timeit(uuid4_id, number=100_000))
print("secrets:", timeit.timeit(secrets_id, number=100_000))
