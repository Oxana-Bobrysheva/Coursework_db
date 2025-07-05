from dotenv import load_dotenv
import os
from db_manager import DBManager

def main():
    load_dotenv()

    db = DBManager(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432))
    )
    db.create_tables()
    print("Таблицы созданы")
    db.close()

if __name__ == "__main__":
    main()