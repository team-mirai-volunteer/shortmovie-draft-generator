from pydantic_settings import BaseSettings
from agents import set_default_openai_key


class EnvSetting(BaseSettings):
    OPENAI_API_KEY: str = ""

    # SQLiteでデータ管理をする場合
    SQLITE_DATABASE: str = "test.db"

    # MySQLでデータ管理する場合
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = ""
    MYSQL_READ_ONLY_HOST: str = ""
    MYSQL_DATABASE: str = ""

    class Config:
        env_file = ".env.local"


env_setting = EnvSetting()
set_default_openai_key(env_setting.OPENAI_API_KEY, use_for_tracing=True)
