import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


def database_url():
    return URL.create(
        "mysql+mysqlconnector", username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"], host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")), database=os.environ["DB_NAME"],
    )
