import sys


# https://github.com/python/mypy/issues/1393 is fixed
if sys.version_info < (3, 10):
    # compatibility for python <3.10
    import importlib_metadata as metadata
else:
    from importlib import metadata

__version__ = metadata.version("pillar")
