"""AGER translation layer — OKF graphs to framework projects."""

__version__ = "0.1.0"

from .cli import compile_graph, TARGETS

__all__ = ["compile_graph", "TARGETS", "__version__"]
