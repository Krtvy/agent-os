"""In-process TTL cache for slow read-only computed views.

Use as `@cached(ttl_seconds=60)` on functions whose result only
depends on their arguments and which are expensive enough that a
60-second staleness window is a great trade.

Properties:
- Process-local — wiped on restart (no persistence, no Redis dep).
- Thread-safe via a single lock around the dict.
- Per-function namespace via (module, qualname).
- Cache keys must be hashable: pass primitives, dates, strings.
- TTL bypass: clear() wipes everything (e.g. on hot-reload during dev).

Trade-off: a stale-cached page can be served for up to TTL seconds
after the underlying data changes. For /standup, /creators, /coordinator,
/dashboard this is fine — POCs refreshing every minute see fresh
data; the cache only saves work on rapid repeated views.

DO NOT use this on functions whose result depends on POC-edited
state (trackers, roster). Their data has to be fresh on every edit.
"""

from __future__ import annotations

import threading
import time
from functools import wraps
from typing import Any, Callable

_STORE: dict[tuple, tuple[float, Any]] = {}
_LOCK = threading.Lock()
_HITS = 0
_MISSES = 0


def cached(ttl_seconds: int = 300, key_fn: Callable | None = None):
    """Cache fn's result by args for `ttl_seconds`.

    Default key: (fn.__module__, fn.__qualname__, args, sorted(kwargs)).
    Pass `key_fn(*args, **kwargs) -> tuple` to override.
    """
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            global _HITS, _MISSES
            if key_fn is not None:
                key = (fn.__module__, fn.__qualname__, key_fn(*args, **kwargs))
            else:
                key = (fn.__module__, fn.__qualname__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            with _LOCK:
                entry = _STORE.get(key)
                if entry is not None and (now - entry[0]) < ttl_seconds:
                    _HITS += 1
                    return entry[1]
                _MISSES += 1
            # Compute outside the lock so a slow function doesn't block
            # other threads looking up other keys. A small race where two
            # threads both miss + recompute the same key is acceptable.
            result = fn(*args, **kwargs)
            with _LOCK:
                _STORE[key] = (time.time(), result)
            return result
        return wrapper
    return deco


def clear() -> None:
    """Wipe the entire cache."""
    with _LOCK:
        _STORE.clear()


def stats() -> dict:
    with _LOCK:
        return {
            "entries": len(_STORE),
            "hits": _HITS,
            "misses": _MISSES,
            "hit_rate": (_HITS / (_HITS + _MISSES)) if (_HITS + _MISSES) else 0.0,
        }
