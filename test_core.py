import unittest
from concurrent.futures import ThreadPoolExecutor

from core import TokenBucket


class Tests(unittest.TestCase):
    def test_refill_and_retry(self):
        now = [0]
        b = TokenBucket(3, 2, lambda: now[0])
        self.assertTrue(b.consume(3).allowed)
        self.assertEqual(b.consume().retry_after, 0.5)
        now[0] = 0.25
        self.assertEqual(b.consume().retry_after, 0.25)
        now[0] = 0.5
        self.assertTrue(b.consume().allowed)
        now[0] = 100
        self.assertEqual(b.consume().remaining, 2)

    def test_atomic_burst(self):
        b = TokenBucket(10, 1, lambda: 0)
        with ThreadPoolExecutor(max_workers=8) as p:
            self.assertEqual(
                sum(d.allowed for d in p.map(lambda _: b.consume(), range(100))), 10
            )

    def test_bad_cost_and_clock_rollback(self):
        b = TokenBucket(1, 1, lambda: 0)
        for cost in [0, -1, 2, float("nan")]:
            with self.assertRaises(ValueError):
                b.consume(cost)
        b.consume()
        b.clock = lambda: -5
        self.assertFalse(b.consume().allowed)


if __name__ == "__main__":
    unittest.main()
