import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "insecure-default-key")
    TEMPLATES_AUTO_RELOAD = False
    LOG_LEVEL = "INFO"


class DevConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    LOG_LEVEL = "DEBUG"


class ProdConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    LOG_LEVEL = "INFO"
