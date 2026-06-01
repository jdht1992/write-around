from functools import lru_cache
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn 
    REDIS_URL: RedisDsn

    #postgres_user: str
    #postgres_password: str
    #postgres_db: str
    
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    @property
    def async_database_url(self) -> str:
        # Converting to string right here is the "clean" way
        return str(self.DATABASE_URL)

    @property
    def async_redis_url(self) -> str:
        return str(self.REDIS_URL)


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
