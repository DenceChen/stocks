"""
Stock Investment Agent Package
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "StockAgent":
        from .stock_agent import StockAgent
        return StockAgent
    elif name == "get_config":
        from .config import get_config
        return get_config
    elif name == "Logger":
        from .utils import Logger
        return Logger
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__version__ = "1.0.0" 