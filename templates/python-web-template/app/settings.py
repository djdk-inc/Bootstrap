import os


class Settings:
    app_secret: str = os.getenv("APP_SECRET", "")


settings = Settings()
