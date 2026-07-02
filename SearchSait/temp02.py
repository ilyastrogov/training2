import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
import urllib.parse

class OfontDownloader:
    def __init__(self, download_folder="downloaded_fonts"):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.base_url = "https://ofont.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _encode_url(self, url):
        """Кодирует URL, заменяя кириллические символы на percent‑encoding."""
        parsed = urllib.parse.urlparse(url)
        encoded_path = urllib.parse.quote(parsed.path.encode('utf-8'))
        encoded_query = urllib.parse.quote(parsed.query.encode('utf-8') if parsed.query else '')
        encoded_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            encoded_path,
            parsed.params,
            encoded_query,
            parsed.fragment
        ))
        return encoded_url

    def find_download_link(self, font_name="Monotype Corsiva"):
        """Ищет реальную ссылку для скачивания шрифта."""
        try:
            # print(f"Загружаем страницу: {self.search_url}")
            # response = self.session.get(self.search_url, timeout=10)
            # response.raise_for_status()

            search_query = urllib.parse.quote(font_name)
            search_url = f"{self.base_url}/search/?q={search_query}"

            print(f"Загружаем страницу поиска: {search_url}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем прямые ссылки на .ttf файлы
            ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
            print('1', ttf_links)
            for link in ttf_links:
                href = link.get('href')
                if href and not href.startswith('#'):
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = href
            # Кодируем URL перед возвратом
                    return self._encode_url(full_url)

            # Если прямых ссылок нет, ищем кнопки модальных окон
            modal_buttons = soup.find_all('a', {'data-bs-toggle': 'modal'})
            for button in modal_buttons:
                font_id = button.get('data-font')
                if font_id:
                    direct_download_url = f"{self.base_url}/download/font/{font_id}"
            # Проверяем доступность ссылки
                    test_response = self.session.head(
                        direct_download_url,
                        allow_redirects=True,
                        timeout=10
                    )
                    if test_response.status_code in [200, 302]:
                        print(f"Найден потенциальный URL: {direct_download_url}")
                        return self._encode_url(direct_download_url)

                print("Не удалось найти прямую ссылку для скачивания")
                return None
        except Exception as e:
            print(f"Ошибка при поиске ссылки: {e}")
            return None

    # def find_download_link(self, font_name="Monotype Corsiva"):
    #     """Ищет ссылку для скачивания шрифта по названию."""
    #     try:
    #         # Формируем поисковый запрос
    #         search_query = urllib.parse.quote(font_name)
    #         search_url = f"{self.base_url}/search/?q={search_query}"
    #
    #         print(f"Загружаем страницу поиска: {search_url}")
    #         response = self.session.get(search_url, timeout=10)
    #         response.raise_for_status()
    #
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #
    #         # Ищем ссылки на страницы шрифтов
    #         font_links = soup.find_all('a', href=re.compile(r'/font/'))
    #         print('2', font_links)
    #         for link in font_links:
    #             href = link.get('href')
    #             if href and font_name.lower() in link.get_text().lower():
    #                 font_page_url = urllib.parse.urljoin(self.base_url, href)
    #                 print(f"Найдена страница шрифта: {font_page_url}")
    #
    #                 # Переходим на страницу шрифта
    #                 font_response = self.session.get(font_page_url, timeout=10)
    #                 font_response.raise_for_status()
    #                 font_soup = BeautifulSoup(font_response.text, 'html.parser')
    #
    #         # Ищем кнопку/ссылку скачивания
    #                 download_button = font_soup.find('a', string=re.compile(r'скачать', re.IGNORECASE))
    #                 print('2',download_button)
    #                 if download_button:
    #                     download_href = download_button.get('href')
    #                     if download_href:
    #                         full_download_url = urllib.parse.urljoin(font_page_url, download_href)
    #                         return self._encode_url(full_download_url)
    #
    #         # Альтернативный поиск: ссылки с расширением .ttf/.otf
    #                 file_links = font_soup.find_all('a', href=re.compile(r'\.(ttf|otf)$', re.IGNORECASE))
    #                 for file_link in file_links:
    #                     file_href = file_link.get('href')
    #                     if file_href:
    #                         full_file_url = urllib.parse.urljoin(font_page_url, file_href)
    #                         return self._encode_url(full_file_url)
    #
    #         print("Не удалось найти ссылку для скачивания на странице шрифта")
    #         return None
    #
    #     except Exception as e:
    #         print(f"Ошибка при поиске ссылки: {e}")
    #         return None

    def download_font(self, link, filename=None):
        """Скачивает шрифт по найденной ссылке."""
        try:
            if not link or link.startswith('#') or link.startswith('javascript:'):
                print("Недопустимая ссылка для скачивания")
                return False

            print(f"Скачиваем шрифт по ссылке: {link}")

            response = self.session.get(
                link,
                stream=True,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()

            # Определяем имя файла из заголовка Content-Disposition или URL
            content_disposition = response.headers.get('content-disposition')
            if content_disposition and 'filename=' in content_disposition:
                filename = re.findall('filename="(.+)"', content_disposition)[0]
            else:
                filename = link.split('/')[-1]
                if not filename.endswith(('.ttf', '.otf')):
                    filename += '.ttf'

            save_path = self.download_folder / filename

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

                    # Проверка размера файла
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

    def run(self, font_name="Monotype Corsiva"):
        """Основной метод для запуска процесса."""
        print(f"Начинаем поиск шрифта '{font_name}'...")

        download_link = self.find_download_link(font_name)
        if not download_link:
            print("Не удалось найти шрифт для скачивания")
            return False

        print(f"Найденная ссылка для скачивания: {download_link}")
        success = self.download_font(download_link)
        return success

# Запуск программы
if __name__ == "__main__":
    downloader = OfontDownloader("my_fonts")
    success = downloader.run("Monotype Corsiva")
    if success:
        print("Программа завершена успешно!")
    else:
        print("Произошла ошибка при скачивании шрифта")
