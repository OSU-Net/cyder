import logging
from django.conf import settings


__all__ = ['patch']


# Idempotence! http://en.wikipedia.org/wiki/Idempotence
_has_patched = False


def patch():
    global _has_patched
    if _has_patched:
        return

    # Import for side-effect: configures logging handlers.
    # pylint: disable-msg=W0611
    import log_settings

    # Monkey-patch django forms to avoid having to use Jinja2's |safe
    # everywhere.
    import safe_django_forms
    safe_django_forms.monkeypatch()

    # Monkey-patch Django's csrf_protect decorator to use session-based CSRF
    # tokens:
    if 'session_csrf' in settings.INSTALLED_APPS:
        import session_csrf
        session_csrf.monkeypatch()
        from . import admin
        admin.monkeypatch()

    if 'compressor' in settings.INSTALLED_APPS:
        import jingo
        from compressor.contrib.jinja2ext import CompressorExtension
        jingo.env.add_extension(CompressorExtension)

    logging.debug("Note: funfactory monkey patches executed in %s" % __file__)

    # prevent it from being run again later
    _has_patched = True
