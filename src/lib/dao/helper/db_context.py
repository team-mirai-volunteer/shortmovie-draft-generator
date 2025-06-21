from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.setting import env_setting


class DBContext:
    def get_read_session(self) -> sessionmaker:
        raise NotImplementedError

    def get_write_session(self) -> sessionmaker:
        raise NotImplementedError


class MySQLDBContext(DBContext):
    def __init__(self, user: str, password: str, host: str, read_only_host: str, db_name: str):
        self._setup(user, password, host, read_only_host, db_name)

    def get_read_session(self) -> sessionmaker:
        return self._read_context()

    def get_write_session(self) -> sessionmaker:
        return self._write_context()

    def _setup(self, user: str, password: str, host: str, read_only_host: str, db_name: str) -> None:
        if not read_only_host:
            read_only_host = host

        self._read_engine = create_engine(
            url=f"mysql+pymysql://{user}:{password}@{read_only_host}/{db_name}",
            pool_recycle=3600,
            pool_pre_ping=True,
        )

        self._write_engine = create_engine(
            url=f"mysql+pymysql://{user}:{password}@{host}/{db_name}",
            pool_recycle=3600,
            pool_pre_ping=True,
        )

        self._read_context = sessionmaker(autocommit=False, autoflush=False, bind=self._read_engine, expire_on_commit=False)
        self._write_context = sessionmaker(autocommit=False, autoflush=False, bind=self._write_engine, expire_on_commit=False)


class SQLiteDBContext(DBContext):
    def __init__(self, db_name: str):
        self._setup(db_name)

    def get_read_session(self) -> sessionmaker:
        return self._read_context()

    def get_write_session(self) -> sessionmaker:
        return self._write_context()

    def _setup(self, db_name: str) -> None:
        self._read_engine = create_engine(f"sqlite:///{db_name}", echo=True)
        self._write_engine = create_engine(f"sqlite:///{db_name}", echo=True)

        self._read_context = sessionmaker(autocommit=False, autoflush=False, bind=self._read_engine, expire_on_commit=False)
        self._write_context = sessionmaker(autocommit=False, autoflush=False, bind=self._write_engine, expire_on_commit=False)


if env_setting.MYSQL_USER:
    db_context: DBContext = MySQLDBContext(
        user=env_setting.MYSQL_USER,
        password=env_setting.MYSQL_PASSWORD,
        host=env_setting.MYSQL_HOST,
        read_only_host=env_setting.MYSQL_READ_ONLY_HOST,
        db_name=env_setting.MYSQL_DATABASE,
    )
else:
    db_context: DBContext = SQLiteDBContext(db_name=env_setting.SQLITE_DATABASE)
