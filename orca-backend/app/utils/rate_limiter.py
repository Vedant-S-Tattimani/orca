"""
Reusable in-memory sliding-window rate limiter for ORCA Backend.

Usage:
    from app.utils.rate_limiter import RateLimiter

    login_limiter = RateLimiter(max_requests=5, window_seconds=900)

    # In a route handler:
    if not login_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many attempts")
"""
import time
from collections import defaultdict, deque


class RateLimiter:
    """
    Sliding-window rate limiter backed by an in-memory deque per key.
    Thread-safe enough for single-process uvicorn (the standard ORCA deployment).
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # key -> deque of timestamps
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        """
        Returns True if the request is within the rate limit, False if it should be rejected.
        Automatically evicts expired timestamps.
        """
        now = time.time()
        window_start = now - self.window_seconds
        q = self._hits[key]

        # Evict timestamps older than the window
        while q and q[0] < window_start:
            q.popleft()

        if len(q) >= self.max_requests:
            return False

        q.append(now)
        return True

    def reset(self, key: str | None = None):
        """Reset rate limit state. If key is None, reset all keys."""
        if key is None:
            self._hits.clear()
        else:
            self._hits.pop(key, None)
