"""Парсим данные  с сайта с фильмыми"""

from lxml import html
import requests
import csv


def parse_movie_info(info_list):
    """Преобразует данные в словарь"""
    cleaned_list = [item.strip() for item in info_list if item.strip()]
    movie_info = {}
    current_key = None
    for item in cleaned_list:
        if ':' in item:
            key, value = item.split(':', 1)
            current_key = key.strip()
            movie_info[current_key] = value.strip()
        else:
            if current_key:
                movie_info[current_key] += ', ' + item
    return movie_info


def clean_values(dirty_dictionary):
    """Очищает данные от лишних значков"""
    cleaned_dict = {}
    for key, value in dirty_dictionary.items():
        value = value.strip()
        value = value.replace(',,', '')
        if value.startswith(','):
            value = value[1:]
        cleaned_dict[key] = value.strip()
    return cleaned_dict


def write_to_csv(file_path, data):
    """Запись в csv"""
    fieldnames = set()
    for d in data:
        fieldnames.update(d.keys())
    fieldnames = sorted(fieldnames)

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "CriOS/122.0.6261.62 Mobile/15E148 Safari/604.1"
    }

    number_page = 1
    url = "https://go.utorr.cc/"
    """Определяем количество страниц для парсинга"""
    number_of_pages = int(input("Введите количество страниц для анализа: "))
    items_list = []

    while number_page <= number_of_pages:
        response = requests.get(url + f'page/{number_page}/', headers=headers)
        dom = html.fromstring(response.text)

        items = dom.xpath("//div[@class='post']")
        for item in items:
            item_info = {}
            name = item.xpath(".//div[@class='post-title']/a/text()")  # получаем название фильма
            link = item.xpath(".//div[@class='post-title']/a/@href")  # ссылку на фильм
            desc = item.xpath(".//td//text()")  # получаем данные о фильме
            movie_dict = parse_movie_info(desc)
            desc_dict = clean_values(movie_dict)

            item_info['name'] = str(name[0])
            item_info['link'] = link
            item_info.update(desc_dict)
            # Фильтруем данные:
            keys_to_keep = ['link', 'name', 'Актеры', 'Время', 'Год', 'Жанр', 'Режиссер', 'Слоган', 'Страна']
            filtered_dict = {key: item_info[key] for key in keys_to_keep if key in item_info}

            items_list.append(filtered_dict)
        number_page += 1

    write_to_csv("utorr.csv", items_list)
