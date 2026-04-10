from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str
    APP_ENV: str

    # База данных
    DATABASE_URL: str
    
    # Telegram
    BOT_TOKEN: str

    # URL домена (для формирования ссылок)
    BASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
