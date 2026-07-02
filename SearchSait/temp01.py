import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
import time

class MonotypeCorsivaDownloader:
    def __init__(self, download_folder="downloaded_fonts"):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.base_url = "https://всешрифты.рф"
        self.search_url = f"{self.base_url}/fonts/besplatnye-shrifty/monotype-corsiva/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def find_download_link(self):
        """Ищет реальную ссылку для скачивания шрифта."""
        try:
            print(f"Загружаем страницу: {self.search_url}")
            response = self.session.get(self.search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Вариант 1: ищем прямые ссылки на .ttf файлы
            ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
            for link in ttf_links:
                href = link.get('href')
                if href and not href.startswith('#'):
                    if href.startswith('/'):
                        return f"{self.base_url}{href}"
                return href

            # Вариант 2: ищем кнопки с атрибутом download
            download_links = soup.find_all('a', attrs={'download': True})
            for link in download_links:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        return f"{self.base_url}{href}"
                return href

            # Вариант 3: анализируем кнопки модальных окон с данными для скачивания
            modal_buttons = soup.find_all('a', {
                'data-bs-toggle': 'modal',
                'data-bs-target': re.compile(r'modal', re.IGNORECASE)
            })
            for button in modal_buttons:
                # Пытаемся извлечь ID шрифта или другие данные
                font_id = button.get('data-font')
                if font_id:
                    # Формируем потенциальную ссылку для скачивания
                    direct_download_url = f"{self.base_url}/download/font/{font_id}"
                    # Проверяем, доступна ли ссылка
                    test_response = self.session.head(direct_download_url, allow_redirects=True)
                    if test_response.status_code in [200, 302]:
                        print(f"Найден потенциальный URL через data-font: {direct_download_url}")
                        return direct_download_url

            # Вариант 4: ищем скрытые ссылки в скриптах страницы
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text()
                # Ищем URL в JavaScript‑коде
                ttf_matches = re.findall(r'["\'](https?://[^"\']*\.ttf[^"\']*)["\']', script_text, re.IGNORECASE)
                if ttf_matches:
                    return ttf_matches[0]

            print("Не удалось найти прямую ссылку для скачивания")
            return None
        except Exception as e:
            print(f"Ошибка при поиске ссылки: {e}")
            return None

    def download_font(self, link, filename="Monotype_Corsiva.ttf"):
        """Скачивает шрифт по найденной ссылке."""
        try:
            if not link or link.startswith('#') or link.startswith('javascript:'):
                print("Недопустимая ссылка для скачивания")
                return False

            print(f"Начинаем скачивание: {link}")
            response = self.session.get(link, stream=True, timeout=30)
            response.raise_for_status()

            save_path = self.download_folder / filename

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Шрифт успешно скачан: {save_path}")
            return True
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return False

    def run(self):
        """Основной метод для запуска процесса."""
        print("Начинаем поиск шрифта Monotype Corsiva...")

        download_link = self.find_download_link()
        if not download_link:
            print("Не удалось найти шрифт для скачивания")
            return False

        print(f"Найденная ссылка для скачивания: {download_link}")
        success = self.download_font(download_link)
        return success

# Запуск программы
if __name__ == "__main__":
    downloader = MonotypeCorsivaDownloader("my_fonts")
    success = downloader.run()
    if success:
        print("Программа завершена успешно!")
    else:
        print("Произошла ошибка при скачивании шрифта")
