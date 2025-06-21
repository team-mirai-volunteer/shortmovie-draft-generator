from functools import wraps
from sqlalchemy.exc import OperationalError
from src.lib.dao.helper.db_context import db_context


def auto_session_manage(mode="read", retry_times=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = kwargs.get("session", None)
            retried = 0

            while retried < retry_times:
                try:
                    if session is None:
                        if mode == "write":
                            session = db_context.get_write_session()
                        else:
                            session = db_context.get_read_session()
                        kwargs["session"] = session
                    return func(*args, **kwargs)
                except OperationalError as oe:
                    retried += 1
                    if session:
                        # rollback the session
                        session.rollback()
                        # close the session and force to get a new one
                        session.close()
                        session = None
                    if retried == retry_times:
                        raise oe

                except Exception as e:
                    if session:
                        # rollback the session
                        session.rollback()
                    raise e

                finally:
                    if session:
                        # automatically close the session
                        session.close()

        return wrapper

    return decorator
