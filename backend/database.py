from dotenv import load_dotenv
import os, psycopg2

load_dotenv()

# psycopg2: PostgreSQL adapter for python, lets python code interact with postgreSQL db w/ raw SQL
# We are creating a live connection to the db
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
         dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )