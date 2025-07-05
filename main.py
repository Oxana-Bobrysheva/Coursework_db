import os
import psycopg2
from dotenv import load_dotenv
from db_manager import DBManager
import requests

def get_vacancies_by_keyword(keyword: str, max_vacancies: int = 100) -> list:
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "per_page": 20,
        "page": 0
    }
    vacancies = []
    while len(vacancies) < max_vacancies:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        vacancies.extend(data['items'])
        if params['page'] >= data['pages'] - 1:
            break
        params['page'] += 1
    return vacancies[:max_vacancies]

def extract_employers_and_vacancies(vacancies):
    employers = {}
    vacancies_list = []

    for vac in vacancies:
        emp = vac.get('employer')
        if not emp:
            # Нет работодателя — пропускаем
            continue
        emp_id = emp.get('id')
        if not emp_id:
            # Нет id работодателя — пропускаем
            continue
        try:
            emp_id = int(emp_id)
        except (TypeError, ValueError):
            continue

        if emp_id not in employers:
            employers[emp_id] = {
                'id': emp_id,
                'name': emp.get('name', 'Unknown'),
                'url': emp.get('url', '')
            }

        salary = vac.get('salary')
        salary_from = salary.get('from') if salary else None
        salary_to = salary.get('to') if salary else None
        salary_currency = salary.get('currency') if salary else None
        area_name = vac.get('area', {}).get('name', '')
        vacancy_data = {
            'id': int(vac['id']),
            'name': vac.get('name', ''),
            'employer_id': emp_id,
            'salary_from': salary_from,
            'salary_to': salary_to,
            'salary_currency': salary_currency,
            'area_name': area_name,
            'url': vac.get('alternate_url', '')
        }
        vacancies_list.append(vacancy_data)

    return employers, vacancies_list

def main():
    load_dotenv()
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    db = DBManager(connection)
    db.create_tables()
    # Запрос ключевого слова у пользователя
    keyword = input("Введите ключевое слово для поиска вакансий: ").strip()
    print(f"Получаем вакансии по ключевому слову '{keyword}'...")

    vacancies = get_vacancies_by_keyword(keyword, max_vacancies=100)
    employers, vacancies_list = extract_employers_and_vacancies(vacancies)

    print(f"Найдено работодателей: {len(employers)}")
    print(f"Найдено вакансий: {len(vacancies_list)}")

    # Заполняем таблицы
    for emp in employers.values():
        db.insert_employer(emp)
    for vac in vacancies_list:
        db.insert_vacancy(vac)

    print("\nДанные успешно загружены в базу.\n")

    # Вызов методов класса DBManager для вывода информации
    print("Компании и количество вакансий:")
    for row in db.get_companies_and_vacancies_count():
        print(f"{row[0]} — {row[1]} вакансий")

    print("\nВсе вакансии:")
    for vac in db.get_all_vacancies():
        print(f"{vac[1]} | {vac[0]} | {vac[2]} — {vac[3]}")

    avg_salary = db.get_avg_salary()
    print(f"\nСредняя зарплата по вакансиям: {avg_salary}")

    print("\nВакансии с зарплатой выше средней:")
    for vac in db.get_vacancies_with_higher_salary():
        print(f"{vac[1]} | {vac[0]} | {vac[2]} — {vac[3]}")

    keyword_for_search = input("\nВведите ключевое слово для поиска в названиях вакансий: ").strip()
    print(f"Вакансии, содержащие '{keyword_for_search}':")
    for vac in db.get_vacancies_with_keyword(keyword_for_search):
        print(f"{vac[1]} | {vac[0]} | {vac[2]} — {vac[3]}")

    connection.close()

if __name__ == "__main__":
    main()
