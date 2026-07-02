import os
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

import re

class FontDownloader:
    def __init__(self, download_folder="downloaded_fonts"):
        """Инициализация загрузчика шрифтов."""
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)

    def download_font_from_url(self, font_url, custom_filename=None):
        """Скачивает шрифт по прямой ссылке."""
        try:
            response = requests.get(font_url, stream=True, timeout=30)
            response.raise_for_status()

            # Определяем имя файла
            if custom_filename:
                filename = custom_filename
            else:
                # Берём имя из URL
                parsed_url = urlparse(font_url)
                filename = os.path.basename(parsed_url.path)
                if not filename.lower().endswith('.ttf'):
                    filename = f"{custom_filename or 'font'}.ttf"

            save_path = self.download_folder / filename

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Шрифт успешно скачан: {save_path}")
            return True
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return False

    def search_yandex_fonts(self, font_name):
        """
        Ищет шрифты на Yandex (упрощённый поиск).
        В реальности может потребоваться использование API или парсинг страниц.
        """
        print(f"Поиск шрифта '{font_name}' на Yandex...")

        # Упрощённый подход: формируем поисковый запрос
        search_url = f"https://yandex.ru/search/?text={font_name}+шрифт+ttf"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Ошибка поиска: HTTP {response.status_code}")

            # Ищем прямые ссылки на .ttf в HTML
            ttf_links = self._extract_ttf_links(response.text)
            return ttf_links
        except Exception as e:
            print(f"Ошибка при поиске на Yandex: {e}")
            return []

    def _extract_ttf_links(self, html_content):
        """Извлекает ссылки на .ttf файлы из HTML."""
        pattern = r'https?://[^"\']*\.ttf(?:\?[^"\']*)?'
        links = re.findall(pattern, html_content)
        print('links', html_content)
        return links

    def download_from_specific_sites(self, font_name, sites, custom_filename=None):
        """
        Скачивает шрифт с указанных сайтов.

        Args:
            font_name (str): Название шрифта.
            sites (list): Список URL сайтов для поиска.
            custom_filename (str, optional): Имя для сохранения файла.
        """
        for site_url in sites:
            print(f"Поиск на сайте: {site_url}")
            try:
                response = requests.get(site_url, timeout=10)
                response.raise_for_status()
                ttf_links = self._extract_ttf_links(response.text)
                if ttf_links:
                    # Скачиваем первый найденный шрифт
                    return self.download_font_from_url(ttf_links[0], custom_filename)
                else:
                    print(f"На сайте {site_url} не найдено .ttf файлов.")
            except Exception as e:
                print(f"Ошибка доступа к {site_url}: {e}")
        return False

# Пример использования
if __name__ == "__main__":
    downloader = FontDownloader("my_fonts")

    # Вариант 1: скачать с конкретного URL
    direct_url = "https://example.com/fonts/BrushScript.ttf"
    downloader.download_font_from_url(direct_url, "my_brush_script.ttf")

    # Вариант 2: поиск на Yandex и скачивание
    font_to_search = "Monotype Corsiva"
    yandex_links = downloader.search_yandex_fonts(font_to_search)
    if yandex_links:
        print("Найдены ссылки:")
        for i, link in enumerate(yandex_links[:3], 1):
            print(f"{i}. {link}")
        # Скачиваем первый результат
        downloader.download_font_from_url(yandex_links[0], f"{font_to_search}.ttf")
    else:
        print("Шрифты не найдены на Yandex.")


    # Вариант 3: поиск на конкретных сайтах
    sites_to_check = [
        "https://всешрифты.рф/fonts/besplatnye-shrifty/monotype-corsiva/",
        "https://www.1001freefonts.com"
    ]
    downloader.download_from_specific_sites(
        "Comic Sans",
        sites_to_check,
        "comic_sans_ms.ttf"
    )
