import os
from dotenv import load_dotenv

load_dotenv()

def get_database():
    engine = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")

    if "postgresql" in engine:
        return {
            "default": {
                "ENGINE": engine,
                "NAME": os.getenv("POSTGRES_DB"),
                "USER": os.getenv("POSTGRES_USER"),
                "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
                "HOST": os.getenv("POSTGRES_HOST"),
                "PORT": os.getenv("POSTGRES_PORT"),
            }
        }

    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.getenv("DB_NAME", "db.sqlite3"),
        }
    }
