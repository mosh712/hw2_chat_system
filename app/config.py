import os

class Config:
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL', 'http://localhost:8000')
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
    CACHE_LAST_X_MESSAGES = int(os.getenv('CACHE_LAST_X_MESSAGES', 10))
    DB_LAST_Y_MESSAGES = int(os.getenv('DB_LAST_Y_MESSAGES', 50))
    S3_RETENTION_DAYS = int(os.getenv('S3_RETENTION_DAYS', 365))
    DB_LIMIT = int(os.getenv('DB_LIMIT', 1000))
    DYNAMODB_REGION = os.getenv('DYNAMODB_REGION', 'us-west-2')

config = Config()
