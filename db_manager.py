class DBManager:
    def __init__(self, connection):
        self.connection = connection

    def create_tables(self):
        with self.connection.cursor() as cur:
            cur.execute(
                """
                DROP TABLE IF EXISTS employers;
                CREATE TABLE IF NOT EXISTS employers (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT
                );
            """
            )
            cur.execute(
                """
                DROP TABLE IF EXISTS vacancies;
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    employer_id INTEGER REFERENCES employers(id),
                    name TEXT NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    salary_currency TEXT,
                    area_name TEXT,
                    url TEXT
                );
            """
            )
        self.connection.commit()
        print("Таблицы employers и vacancies созданы (если их не было).")

    def insert_employer(self, employer: dict):
        """
        Insert an employer into the employers table.
        employer dict should have keys: id, name, url
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employers (id, name, url)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
                (employer["id"], employer["name"], employer["url"]),
            )
        self.connection.commit()

    def insert_vacancy(self, vacancy: dict):
        """
        Insert a vacancy into the vacancies table.
        vacancy dict keys:
        id, name, employer_id, salary_from, salary_to,
        salary_currency, area_name, url
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vacancies (
                    id, name, employer_id, salary_from, salary_to,
                    salary_currency, area_name, url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
                (
                    vacancy["id"],
                    vacancy["name"],
                    vacancy["employer_id"],
                    vacancy["salary_from"],
                    vacancy["salary_to"],
                    vacancy["salary_currency"],
                    vacancy["area_name"],
                    vacancy["url"],
                ),
            )
        self.connection.commit()

    def get_companies_and_vacancies_count(self):
        """
        Return list of tuples (company_name, vacancies_count)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, COUNT(v.id)
                FROM employers e
                LEFT JOIN vacancies v ON e.id = v.employer_id
                GROUP BY e.name
                ORDER BY e.name
            """
            )
            return cursor.fetchall()

    def get_all_vacancies(self):
        """
        Return list of tuples (vacancy_name, company_name, salary_from, url)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT v.name, e.name, v.salary_from, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                ORDER BY v.name
            """
            )
            return cursor.fetchall()

    def get_avg_salary(self):
        """
        Return average of (salary_from + salary_to)/2
        for vacancies with both salaries set
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG((salary_from + salary_to)/2.0)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
            """
            )
            avg_salary = cursor.fetchone()[0]
            return avg_salary if avg_salary is not None else 0

    def get_vacancies_with_higher_salary(self):
        """
        Return vacancies where average salary > overall average salary.
        Returns list of tuples (vacancy_name, company_name, salary_from, url)
        """
        avg_salary = self.get_avg_salary()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT v.name, e.name, v.salary_from, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0))/2 > %s
                ORDER BY v.salary_from DESC NULLS LAST
            """,
                (avg_salary,),
            )
            return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str):
        """
        Return vacancies where vacancy name contains
        the keyword (case-insensitive).
        Returns list of tuples
        (vacancy_name, company_name, salary_from, url)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT v.name, e.name, v.salary_from, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.name ILIKE %s
                ORDER BY v.name
            """,
                (f"%{keyword}%",),
            )
            return cursor.fetchall()
