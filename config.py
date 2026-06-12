import os

# python-dotenv is only installed locally. In production on Render the package
# does not exist, so the import is wrapped to fail silently - Render supplies
# environment variables through its dashboard instead of a .env file.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class DevelopmentConfig:
    # Local development continues to use the local MySQL database.
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:1234@localhost/mechanic_shop_v3'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'


class TestingConfig:
    # Tests use an in-memory SQLite database, same as the test setUp methods did before.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    CACHE_TYPE = 'SimpleCache'


class ProductionConfig:
    # Production reads the database URI from the environment.
    # os.environ.get returns the value of the named variable, or None if it does not exist.
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CACHE_TYPE = 'SimpleCache'