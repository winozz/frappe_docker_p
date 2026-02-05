"""Minimal frappe shim for local unit tests.
This stub provides the small surface area used by unit tests (throw, logger, ValidationError).
Do not treat this as full frappe; it's only for running isolated unit tests.
"""
class ValidationError(Exception):
    pass


class PermissionError(Exception):
    pass


def throw(message, title=None, exc=ValidationError):
    """Raise an exception similar to frappe.throw"""
    if exc:
        raise exc(message)
    raise Exception(message)


class _Logger:
    def __init__(self, name):
        self.name = name

    def debug(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None


def logger(name=None):
    return _Logger(name)


# Minimal DB stubs used by some validators (exists used rarely in tests)
class _DB:
    def exists(self, *args, **kwargs):
        return False

db = _DB()
