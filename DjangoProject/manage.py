#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Temporary monkey patch for Python 3.14 + Django 4.2 template context copy issue
# Remove after downgrading to supported Python (3.11/3.12)
try:
    import django.template.context as _ctx

    def _ctx_copy(self):
        # RequestContext requires request positional arg; fallback to BaseContext otherwise
        if hasattr(self, "request"):
            dup = self.__class__(self.request)
        else:
            dup = self.__class__()
        dup.dicts = list(getattr(self, "dicts", []))
        dup.autoescape = getattr(self, "autoescape", True)
        dup.use_l10n = getattr(self, "use_l10n", True)
        dup.use_tz = getattr(self, "use_tz", True)
        dup.render_context = getattr(self, "render_context", None)
        return dup

    _ctx.BaseContext.__copy__ = _ctx_copy
    _ctx.Context.__copy__ = _ctx_copy
except Exception:
    # If patch fails, proceed; app may still fail on incompatible Python
    pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
