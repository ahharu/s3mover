import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(os.getenv("DB_USER"),os.getenv("MYSQL_ROOT_PASSWORD"),os.getenv("DB_URI"),os.getenv("MYSQL_DATABASE"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(
    dev=DevelopmentConfig,
)


class ConfigFactory():
    def create_config(self, environment):
        return config_by_name[environment]()
