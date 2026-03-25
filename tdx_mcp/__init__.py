__all__ = ['mcp', 'main']

def __getattr__(name):
    if name == 'mcp':
        from .mcpServer import mcp
        return mcp
    elif name == 'main':
        from .mcpServer import main
        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
