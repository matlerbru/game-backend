from random import randint
import os

def generate_secret(length: int = 64) -> str:
    return "".join([hex(randint(0, 15))[2:] for _ in range(length)])

config = {
    "logging": {
        "path": os.getenv("LOGGING_PATH", default = "game_backend.log"),
        "level": os.getenv("LOGGING_LEVEL", default= "DEBUG")
    },
    "database": {
        "host": os.getenv("DATABASE_HOST", default="mysql_db"),
        "name": os.getenv("DATABASE_NAME", default="game_backend"),
        "user": os.getenv("DATABASE_USER", default="root"),
        "password": os.getenv("DATABASE_PASSWORD", default="root"),
        "port": int(os.getenv("DATABASE_PORT", default="3306")),
        "connection_limit": int(os.getenv("DATABASE_CONNECTION_LIMIT", default="20"))
    },
    "authorization": {
        "secret_key": os.getenv("AUTHORIZATION_SECRET_KEY", generate_secret()),
        "algorithm": os.getenv("AUTHORIZATION_ALGORITHM", default="HS256"),
        "token_expire_time": int(os.getenv("AUTHORIZATION_TOKEN_EXPIRE_TIME", default="30"))
    }
}