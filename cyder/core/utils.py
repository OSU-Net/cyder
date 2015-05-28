import smtplib
import syslog
from email.mime.text import MIMEText

from django.conf import settings

from cyder.base.utils import format_exc_verbose


# Reference http://dev.mysql.com/doc/refman/5.0/en/miscellaneous-functions.html
# TODO, use this on all views touching DNS stuff
def locked_function(lock_name, timeout=10):
    """
    This is a decorator that should be used around any view or function that
    modifies, creates, or deletes a DNS model.
    It's purpose is to prevent this case:

        http://people.mozilla.com/~juber/public/t1_t2_scenario.txt

    """
    def decorator(f):
        def new_function(*args, **kwargs):
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(
                "SELECT GET_LOCK('{lock_name}', {timeout});".format(
                    lock_name=lock_name, timeout=timeout
                )
            )
            ret = f(*args, **kwargs)
            cursor.execute(
                "SELECT RELEASE_LOCK('{lock_name}');".format(
                    lock_name=lock_name
                )
            )
            return ret
        return new_function
    return decorator


def fail_mail(content, subject,
              from_=settings.FAIL_EMAIL_FROM,
              to=settings.FAIL_EMAIL_TO):
    """Send email about a failure."""
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = ', '.join(to)
    s = smtplib.SMTP(settings.FAIL_EMAIL_SERVER)
    s.sendmail(from_, to, msg.as_string())
    s.quit()


def mail_if_failure(msg, ignore=()):
    def outer(func):
        def inner(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ignore:
                # Just let the exception through.
                raise
            except Exception:
                # Send mail first.
                error = msg + '\n' + format_exc_verbose()
                self.log(syslog.LOG_ERR, error)
                fail_mail(error, subject=msg)
                with open(self.stop_file, 'w') as f:
                    f.write(error)
                raise
        outer.__name__ = func.__name__
        outer.__doc__ = func.__doc__
        outer.__module__ = func.__module__
        return inner
    return outer
