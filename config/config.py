






class Config:
    BASE_URL = 'http://localhost:8000'
    TIMEOUT = 10


class TestConfig(Config):
    pass


config = TestConfig()
