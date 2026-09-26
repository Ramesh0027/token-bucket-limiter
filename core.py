import math
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    allowed: bool
    remaining: float
    retry_after: float


class TokenBucket:
    def __init__(self, capacity, rate, clock=time.monotonic):
        if not all(math.isfinite(v) and v > 0 for v in (capacity, rate)):
            raise ValueError("positive finite capacity and rate required")
        self.capacity, self.rate, self.clock = capacity, rate, clock
        self.tokens = float(capacity)
        self.updated = clock()
        self.lock = threading.Lock()

    def consume(self, cost=1):
        if not math.isfinite(cost) or not 0 < cost <= self.capacity:
            raise ValueError("cost must fit capacity")
        with self.lock:
            now = self.clock()
            elapsed = max(0, now - self.updated)
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.updated = max(now, self.updated)
            if self.tokens >= cost:
                self.tokens -= cost
                return Decision(True, self.tokens, 0)
            return Decision(False, self.tokens, (cost - self.tokens) / self.rate)
