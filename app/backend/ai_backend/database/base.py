"""Database module."""

from typing import Any, Callable, Dict, ContextManager
import os
import logging
from pathlib import Path
from contextlib import contextmanager, AbstractContextManager

import pandas as pd

logger = logging.getLogger(__name__)

from sqlalchemy import create_engine, orm
from sqlalchemy.engine import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# 모델 import는 __init__.py에서 처리


__all__ = [
    "Base",
    "Database",
]

Base = declarative_base()


class Database:
    def __init__(self, db_config: Dict[str, Any]) -> None:
        """
        """
        dotted = pd.json_normalize(db_config, sep=".").to_dict(orient='records')[0]
        dotted['database.url'] = 'postgresql://{username}:{password}@{host}:{port}/{dbname}'.format(
            username=os.getenv("DATABASE__USERNAME", os.getenv("SYSTEMDB_USERNAME", dotted.pop("database.username", None))),
            password=os.getenv("DATABASE__PASSWORD", os.getenv("SYSTEMDB_PASSWORD", dotted.pop("database.password", None))),
            host=os.getenv("DATABASE__HOST", dotted.pop("database.host", None)),
            port=os.getenv("DATABASE__PORT", dotted.pop("database.port", None)),
            dbname=os.getenv("DATABASE__DBNAME", dotted.pop("database.dbname", None)),
        )
        self._engine = engine_from_config(dotted, prefix="database.")
        self._session_factory = orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

    def create_database(self, checkfirst: bool = True) -> None:
        """
        테이블 생성
        checkfirst: True면 기존 테이블이 있으면 건너뛰고, False면 무조건 생성 시도
        """
        try:
            Base.metadata.create_all(bind=self._engine, checkfirst=checkfirst)
        except Exception as e:
            raise e

    @contextmanager
    def session(self) -> Callable[..., ContextManager[Session]]:
        """
        """
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if hasattr(self, '_session_factory'):
            self._session_factory.close_all()
        if hasattr(self, '_engine'):
            self._engine.dispose()