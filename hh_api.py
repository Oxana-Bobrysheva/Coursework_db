import requests


def get_vacancies(text, area=1, per_page=20, page=0):
    """
    Получить список вакансий с hh.ru по поисковому запросу.

    :param text: строка поиска (например, "Python developer")
    :param area: регион (1 — Москва по умолчанию)
    :param per_page: кол-во вакансий на странице (максимум 100)
    :param page: номер страницы (начинается с 0)
    :return: список вакансий (json)
    """
    url = "https://api.hh.ru/vacancies"
    params = {"text": text, "area": area, "per_page": per_page, "page": page}
    response = requests.get(url, params=params)
    response.raise_for_status()  # выбросит ошибку, если не 200
    data = response.json()
    return data.get("items", [])


if __name__ == "__main__":
    vacancies = get_vacancies("Python developer")
    print(f"Найдено вакансий: {len(vacancies)}")
    for vac in vacancies[:10]:
        print(vac["name"], "-", vac["employer"]["name"])
