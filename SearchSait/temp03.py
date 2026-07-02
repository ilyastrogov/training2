import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
import urllib.parse
from urllib.parse import urljoin

class MonotypeCorsivaDownloader:
    def __init__(self, download_folder="downloaded_fonts"):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.base_url = "https://ofont.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def find_font_page(self, font_name="Monotype Corsiva"):
        """Ищет страницу шрифта по его названию через поиск на сайте."""
        # search_url = f"{self.base_url}/search"
        # print('search_url', search_url)
        print(f"Загружаем страницу: {self.base_url}")
        response = self.session.get(self.base_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        search_input  = soup.find('input', id='search')
        print('search', search_input)

        # Ищем форму, содержащую это поле
        form = search_input.find_parent('form')
        search_url1 = ''
        if form:
            action_url = form.get('action', '')  # URL для отправки формы
            method = form.get('method', 'GET').upper()  # метод отправки

            # Преобразуем относительный URL в абсолютный

            search_url1 = urljoin(self.base_url, action_url)

            print(f"URL формы поиска: {search_url1}")
            print(f"Метод: {method}")
        else:
            print("Форма не найдена")
        search_url = ''
        params = {'q': font_name}
        response = self.session.get(search_url1, params=params, timeout=10)
        response.raise_for_status()
        print('resp', response.raise_for_status())
        soup = BeautifulSoup(response.text, 'html.parser')

        font_links = soup.find_all('a', href=re.compile(r'/view/\d+'))
        print('ddddd', font_links)

        for link in font_links:

            href = link.get('href')

            pattern = rf'{font_name}'
            match = re.search(pattern, str(link))
            # # Проверяем, что название шрифта содержится в тексте ссылки (нестрогое совпадение)
            if match and href:
                # Формируем полный URL
                if href.startswith('/'):
                    search_url = f"{self.base_url}{href}"
                    print('22', search_url)
        return search_url


    def _make_absolute_url(self, relative_url, base_url):
        """Создаёт абсолютный URL из относительного."""
        if relative_url.startswith('http'):
            return relative_url
        elif relative_url.startswith('/'):
            # Берём домен из base_url
            from urllib.parse import urlparse
            base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
            return f"{base_domain}{relative_url}"
        else:
            # Относительный путь в текущей директории
            return f"{base_url.rsplit('/', 1)[0]}/{relative_url}"

    def find_download_link(self, page_url):
        """Ищет реальную ссылку для скачивания шрифта на указанной странице."""
        try:
            print(f"Загружаем страницу: {page_url}")
            response = self.session.get(page_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Вариант 1: ищем прямые ссылки на .ttf файлы
            ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
            for link in ttf_links:
                href = link.get('href')
                if href and not href.startswith('#'):
                    full_url = self._make_absolute_url(href, page_url)
                    print(f"Прямая ссылка на TTF: {full_url}")
                    return full_url

            # Вариант 2: ищем кнопки скачивания (обычно класс 'btn' или 'download-btn')
            download_buttons = soup.find_all('a', class_=re.compile(r'btn|download', re.IGNORECASE))
            for button in download_buttons:
                href = button.get('href')
                onclick = button.get('onclick')

                if href:
                    full_url = self._make_absolute_url(href, page_url)
                    print(f"Кнопка скачивания: {full_url}")
                    return full_url
                elif onclick and 'download' in onclick.lower():
                    # Иногда ссылка генерируется через JavaScript
                    match = re.search(r"['\"]([^'\"]+)", onclick)
                    if match:
                        js_url = match.group(1)
                        full_url = self._make_absolute_url(js_url, page_url)
                        print(f"Ссылка из JavaScript: {full_url}")
                        return full_url

            # Вариант 3: ищем формы с действием download
            download_forms = soup.find_all('form', action=re.compile(r'download', re.IGNORECASE))
            for form in download_forms:
                action = form.get('action')
                if action:
                    full_url = self._make_absolute_url(action, page_url)
                    print(f"Форма скачивания: {full_url}")
                    return full_url

            print("Не удалось найти ссылку для скачивания")
            return None
        except Exception as e:
            print(f"Ошибка при поиске ссылки: {e}")
            return None

    def download_font(self, link, filename="Monotype_Corsiva.ttf"):
        """Скачивает шрифт по найденной ссылке с проверкой содержимого."""
        try:
            if not link or link.startswith('#') or link.startswith('javascript:'):
                print("Недопустимая ссылка для скачивания")
                return False

            headers = self.session.headers.copy()
            # Не добавляем Referer с кириллицей — это частая причина ошибки
            # headers['Referer'] = self._encode_url(self.search_url)  # Убираем эту строку

            response = self.session.get(
                link,
                stream=True,
                timeout=30,
                headers=headers,
                allow_redirects=True
            )
            response.raise_for_status()

            # Проверка размера файла
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) == 0:
                print("Предупреждение: сервер сообщает о нулевом размере файла")

            save_path = self.download_folder / filename

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Проверка размера скачанного файла
            file_size = save_path.stat().st_size
            if file_size == 0:
                print("Ошибка: файл скачан, но имеет нулевой размер")
                save_path.unlink()  # Удаляем пустой файл
                return False

            print(f"Шрифт успешно скачан: {save_path} (размер: {file_size} байт)")
            return True
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return False

    def run(self, font_name="Monotype Corsiva", filename=None):
        """Основной метод для запуска процесса."""
        print(f"Начинаем поиск шрифта: {font_name}...")

        # Шаг 1: находим страницу шрифта
        font_page_url = self.find_font_page(font_name)
        if not font_page_url:
            print("Не удалось найти страницу шрифта")
            return False

        # Шаг 2: находим ссылку для скачивания на этой странице
        download_link = self.find_download_link(font_page_url)
        if not download_link:
            print("Не удалось найти ссылку для скачивания")
            return False

        print(f"Найденная ссылка для скачивания: {download_link}")

        # Определяем имя файла (если не задано)
        if not filename:
            filename = f"{font_name.replace(' ', '_')}.ttf"

        # Шаг 3: скачиваем шрифт
        success = self.download_font(download_link, filename)
        return success

# Запуск программы
if __name__ == "__main__":
    downloader = MonotypeCorsivaDownloader("my_fonts")
    success = downloader.run("Brush Script Bold")  # Теперь передаём название шрифта
    if success:
        print("Программа завершена успешно!")
    else:
        print("Произошла ошибка при скачивании шрифта")

# загружаем шрифт из сайта
# parts = re.split(r'(?=[A-Z])', font_name)
# font_for_search = ' '.join(word for word in parts if word != '')
# print('normaliz', font_for_search)
# downloader = MonotypeCorsivaDownloader("fonts")
# success = downloader.run(font_for_search)  # Теперь передаём название шрифта
# print(type(success))
# font_id = QFontDatabase.addApplicationFont(str(success))
# if font_id == -1:
#     print("Не удалось загрузить шрифт")
#     return None
#
# # Получаем имя семейства шрифта
# families = QFontDatabase.applicationFontFamilies(font_id)
# if families:
#     family_name = families[0]
#     print(f"Шрифт загружен: {family_name}")
#     return family_name
# else:
#     print("Не удалось получить имя семейства шрифта")
#     return None