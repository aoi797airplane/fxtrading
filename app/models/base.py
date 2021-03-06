from contextlib import contextmanager
import logging
import threading

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import settings

logger = logging.getLogger(__name__)
Base = declarative_base()
engine = create_engine(f'sqlite:///{settings.db_name}?check_same_thread=False')
Session = scoped_session(sessionmaker(bind=engine))
lock = threading.Lock()


# 全然理解していないが、言葉そのまま残しておくと、
# MySQLなどでは設定がもうちょい楽っぽいが、今回はSQLLiteを使うので複雑になりましたよ
# session_scopeでクエリを書き込みますよということ
@contextmanager
def session_scope():
    session = Session()
    session.expire_on_commit = False
    try:
        lock.acquire()
        yield session
        session.commit()
    except Exception as e:
        logger.error(f'action=session_scope error={e}')
        session.rollback()
        raise
    finally:
        lock.release()
        # session.close()


def init_db():
    import app.models.candle
    Base.metadata.create_all(bind=engine)
