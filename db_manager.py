import psycopg2
from psycopg2.extensions import connection, cursor


class DBManager:
    def __init__(self, dbname, user, password, host="localhost", port=5432):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employers (
                    id SERIAL PRIMARY KEY,
                    hh_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    hh_id INTEGER UNIQUE NOT NULL,
                    employer_id INTEGER REFERENCES employers(id),
                    name TEXT NOT NULL,
                    description TEXT,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    area TEXT,
                    url TEXT
                );
            """)

    def add_employer(self, hh_id, name):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employers (hh_id, name)
                VALUES (%s, %s)
                ON CONFLICT (hh_id) DO NOTHING
                RETURNING id;
            """, (hh_id, name))
            res = cur.fetchone()
            if res:
                return res[0]
            else:
                # Если запись уже есть, получим id
                cur.execute("SELECT id FROM employers WHERE hh_id=%s;", (hh_id,))
                return cur.fetchone()[0]

    def add_vacancy(self, hh_id, employer_id, name, description, salary_from, salary_to, area, url):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vacancies (hh_id, employer_id, name, description, salary_from, salary_to, area, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hh_id) DO NOTHING;
            """, (hh_id, employer_id, name, description, salary_from, salary_to, area, url))

    def close(self):
        self.conn.close()
