"""Put code/realdefects/ on sys.path so tests import schema/validator/power directly.

Top-level package name `code` collides with the Python stdlib `code` module,
so the realdefects modules are imported by bare name via this path injection
rather than as a `code.realdefects` package.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REALDEFECTS = os.path.normpath(os.path.join(_HERE, "..", "..", "realdefects"))
if _REALDEFECTS not in sys.path:
    sys.path.insert(0, _REALDEFECTS)
