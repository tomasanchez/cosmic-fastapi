"""
Application Version
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("template")
except PackageNotFoundError:  # pragma: no cover
    # Fallback when the package metadata is unavailable (e.g. running from a
    # source tree without an installed distribution).
    __version__ = "0.0.0"
