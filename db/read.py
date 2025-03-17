from typing import Any, List, Callable, TypeVar, Protocol, Generic
from sqlalchemy.orm import Session, create_session
from db import engine, Feed
from functools import wraps


T = TypeVar('T', covariant=True)

class SessionReciever(Protocol, Generic[T]):
    def __call__(self, session: Session, *args, **kwds: Any) -> T:
        ...

def session_provider(func: SessionReciever[T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        with create_session(bind=engine) as session:
            return func(session, *args, **kwargs)
    return wrapper

@session_provider
def get_feeds(session: Session) -> List[Feed]:
    return session.query(Feed).all()
