from core import TokenBucket

clock = [0]
bucket = TokenBucket(3, 2, lambda: clock[0])
for _ in range(4):
    print(bucket.consume())
clock[0] = 0.5
print("After half a second:", bucket.consume())
