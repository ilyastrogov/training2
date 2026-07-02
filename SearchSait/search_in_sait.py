import os
import requests
from urllib.parse import quote
import re
from pathlib import Path

class FontDownloader:
    def __init__(self, download_folder="downloaded_fonts"):
        """Инициализация загрузчика шрифтов."""
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        # База источников для поиска шрифтов (можно расширить)
        self.font_sources = [
            "https://www.fontsquirrel.com",
            "https://www.1001freefonts.com",
            "https://www.dafont.com",
            'https://всешрифты.рф/fonts/besplatnye-shrifty/monotype-corsiva'
        ]

    def search_and_download_font(self, font_name, custom_filename=None):
        """
        Ищет шрифт по имени и скачивает в указанную папку.

        Args:
            font_name (str): Название шрифта для поиска.
            custom_filename (str, optional): Имя для сохранения файла.
        """
        print(f"Поиск шрифта: {font_name}")

        # Формируем URL для поиска (упрощённо — используем Google)
        search_query = f"{font_name} font .ttf site:fontsquirrel.com OR site:1001freefonts.com OR site:dafont.com"
        encoded_query = quote(search_query)
        google_search_url = f"https://www.google.com/search?q={encoded_query}"

        try:
            # Получаем результаты поиска (в реальности нужно использовать API или парсинг)
            # Для примера — упрощённый подход: ищем прямые ссылки на .ttf в выдаче
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(google_search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Ошибка поиска: HTTP {response.status_code}")
            print(response.text)
            # Ищем ссылки на .ttf файлы в HTML (упрощённо)
            ttf_links = self._extract_ttf_links(response.text)
            if not ttf_links:
                print("Не удалось найти ссылки на .ttf файлы.")
                return False

            # Скачиваем первый найденный .ttf
            download_url = ttf_links[0]
            return self._download_ttf(download_url, font_name, custom_filename)

        except Exception as e:
            print(f"Ошибка при поиске шрифта: {e}")
            return False

    def _extract_ttf_links(self, html_content):
        """Извлекает ссылки на .ttf файлы из HTML."""
        # Регулярное выражение для поиска ссылок с .ttf
        pattern = r'https?://[^"\']*\.ttf(?:\?[^"\']*)?'
        links = re.findall(pattern, html_content)
        return links

    def _download_ttf(self, url, original_name, custom_filename):
        """Скачивает TTF файл и сохраняет с нужным именем."""
        try:
            print(f"Скачивание: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Определяем имя файла
            if custom_filename:
                filename = custom_filename
            else:
                # Берём имя из URL или используем оригинальное имя шрифта
                filename = url.split('/')[-1]
                if not filename.lower().endswith('.ttf'):
                    filename = f"{original_name}.ttf"

            # Полный путь для сохранения
            save_path = self.download_folder / filename

            # Сохраняем файл
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Шрифт сохранён: {save_path}")
            return True

        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return False

# Пример использования
if __name__ == "__main__":
    downloader = FontDownloader("my_fonts")

    # Примеры вызовов:
    # 1. Поиск и скачивание с автоматическим именем
    downloader.search_and_download_font("BrushScript")

    # 2. Поиск и скачивание с кастомным именем
    downloader.search_and_download_font("Monotype Corsiva Normal 400", "my_comic.ttf")
