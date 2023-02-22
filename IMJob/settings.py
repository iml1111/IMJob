import os
from pydantic import BaseSettings, Field


__AUTHOR__ = "IML"
__VERSION__ = "0.1.1"

APP_NAME = "IMJob"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Settings(BaseSettings):

    # Basic settings
    app_name: str = Field(APP_NAME, env="APP_NAME")
    description: str = "IMJob is Boilerplate for Scalable Python Job Workers."
    contact_name: str = __AUTHOR__
    contact_url: str = "https://github.com/iml1111"
    contact_email: str = "shin10256@gmail.com"

    class Config:
        env_file = BASE_DIR + "/.env"
        env_file_encoding = "utf-8"


settings = Settings()