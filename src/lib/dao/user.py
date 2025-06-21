from src.lib.dao.helper.session import auto_session_manage
from src.lib.models.user import User
from sqlalchemy.orm import Session


@auto_session_manage(mode="read")
def get_all_users(session: Session = None) -> list[User] | None:
    if session is None:
        return None
    return session.query(User).all()


@auto_session_manage(mode="read")
def get_user_by_id(user_id: int, session: Session = None) -> User | None:
    if session is None:
        return None
    return session.get(User, user_id)


@auto_session_manage(mode="read")
def get_user_by_email(email: str, session: Session = None) -> User | None:
    if session is None:
        return None
    return session.query(User).filter(User.email == email).first()


@auto_session_manage(mode="write")
def create_user(name: str, email: str, session: Session = None) -> User | None:
    if session is None:
        return None
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    return user


@auto_session_manage(mode="write")
def update_user(user_id: int, name: str, email: str, session: Session = None) -> User | None:
    if session is None:
        return None
    user = session.get(User, user_id)
    if user is None:
        return None
    user.name = name
    user.email = email
    session.commit()
    return user


@auto_session_manage(mode="write")
def delete_user(user_id: int, session: Session = None) -> bool:
    if session is None:
        return False
    user = session.get(User, user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True
