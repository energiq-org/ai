import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

def connect_to_db(mock_db=True):
    if mock_db:
        database_file_path = "ev_charging.db"
        engine = create_engine(f"sqlite:///{database_file_path}")
    
    else:
        DB_HOST     = os.getenv("DB_HOST")
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME     = os.getenv("DB_NAME")
        DB_PORT     = os.getenv("DB_PORT")
        
        DATABASE_URL = (
            f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        engine = create_engine(DATABASE_URL)
         
    return engine

if __name__ == "__main__":
    engine = connect_to_db(False)
    inspector = inspect(engine)

    # List all tables in the public schema
    table_names = inspector.get_table_names()
    print("Tables:", table_names)

    # For each table, list its columns
    for table in table_names:
        columns = inspector.get_columns(table)
        col_names = [col["name"] for col in columns]
        print(f"Table {table!r} columns: {col_names}")
