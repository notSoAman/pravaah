"""
Compatibility fallback for typo in deployment Start Command (config.wgsi -> config.wsgi).
"""

from .wsgi import application

__all__ = ["application"]
