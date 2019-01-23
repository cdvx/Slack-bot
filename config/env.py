from config import get_env

class EnvConfig:
    """ Parent configuration class """

    DEBUG = False
    CSRF_ENABLED = True
    SECRET = get_env("SECRET")


class DevelopmentEnv(EnvConfig):
    """ Development configuration """
    DEBUG = True

class TestingEnv(EnvConfig):
    """ Testing configuration, with a diffrent testing database """
    DEBUG = True
    TESTING = True


class StagingEnv(EnvConfig):
    """ Staging configuration """
    DEBUG = True


class ProductionEnv(EnvConfig):
    """ Prduction configuration """
    DEBUG = True
    TESTING = False

app_env = {
    "development": DevelopmentEnv,
    "testing": TestingEnv,
    "staging": StagingEnv,
    "production": ProductionEnv,
}