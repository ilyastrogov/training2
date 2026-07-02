import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
import urllib.parse
import zipfile

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
        encoded_query = urllib.parse.quote(parsed.query.encode('utf-8'))
        encoded_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            encoded_path,
            parsed.params,
            encoded_query,
            parsed.fragment
        ))
        return encoded_url

    def find_any_font_link(self):
        """Ищет ссылку для скачивания любого шрифта на главной странице."""
        try:
            print(f"Загружаем главную страницу: {self.base_url}")
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем популярные шрифты или новинки
            font_links = soup.find_all('a', href=re.compile(r'/font/\d+', re.IGNORECASE))

            for link in font_links:
                href = link.get('href')
                if href:
                    font_page_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    # Переходим на страницу шрифта
                    font_response = self.session.get(font_page_url, timeout=10)
                    font_soup = BeautifulSoup(font_response.text, 'html.parser')

            # Ищем кнопку скачивания
                    download_btn = font_soup.find('a', {'class': re.compile(r'download|btn', re.IGNORECASE)})
                    if download_btn:
                        download_href = download_btn.get('href')
                        if download_href:
                            potential_url = download_href if download_href.startswith('http') else f"{self.base_url}{download_href}"
            # Проверяем, что это реальная ссылка для скачивания
                            head_response = self.session.head(potential_url, allow_redirects=True, timeout=10)
                            content_type = head_response.headers.get('content-type', '').lower()
                            if 'font' in content_type or 'zip' in content_type:
                                print(f"Найден шрифт: {link.get_text().strip()}")
                                return self._encode_url(potential_url)

            print("Не удалось найти ссылку для скачивания шрифта")
            return None
        except Exception as e:
            print(f"Ошибка при поиске шрифта: {e}")
            return None

    def _verify_ttf_signature(self, file_path):
        """Проверяет сигнатуру TTF‑файла."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
            ttf_signatures = [b'OTTO', b'\x00\x01\x00\x00']
            return any(header == sig for sig in ttf_signatures)
        except:
            return False

    def download_font(self, link, filename="Downloaded_Font.ttf"):
        """Скачивает шрифт по найденной ссылке."""
        try:
            if not link or link.startswith('#') or link.startswith('javascript:'):
                print("Недопустимая ссылка для скачивания")
                return False

            print(f"Исходный URL: {link}")
            encoded_link = self._encode_url(link)
            print(f"Закодированный URL: {encoded_link}")

            headers = self.session.headers.copy()

            # HEAD запрос для проверки
            head_response = self.session.head(encoded_link, allow_redirects=True, timeout=15)
            content_type = head_response.headers.get('content-type', '').lower()
            content_length = head_response.headers.get('content-length')

            print(f"Content-Type: {content_type}")
            print(f"Content-Length: {content_length}")

            allowed_content_types = [
                'application/octet-stream',
                'font/ttf',
                'font/otf',
                'application/x-font-ttf',
                'application/font-woff',
                'application/zip',
                'application/x-zip-compressed'
            ]

            if not any(allowed in content_type for allowed in allowed_content_types):
                print(f"Предупреждение: неожиданный Content-Type: {content_type}")
                print("Ошибка: сервер отдаёт HTML вместо файла — скачивание невозможно")
                return False

            if content_length and int(content_length) == 0:
                print("Сервер сообщает о нулевом размере файла — прерываем скачивание")
                return False

            # Основная загрузка
            response = self.session.get(
                encoded_link,
                stream=True,
                timeout=30,
                headers=headers,
                allow_redirects=True
            )
            response.raise_for_status()

            save_path = self.download_folder / filename

            downloaded_size = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Проверяем, что чанк не пустой
                        f.write(chunk)
                        downloaded_size += len(chunk)

            print(f"Скачано: {downloaded_size} байт")

            # Финальная проверка размера
            file_size = save_path.stat().st_size
            if file_size == 0:
                print("Ошибка: файл скачан, но имеет нулевой размер")
                save_path.unlink()  # Удаляем пустой файл
                return False

            # Если скачан ZIP‑архив, распаковываем
            if save_path.suffix.lower() == '.zip':
                try:
                    with zipfile.ZipFile(save_path, 'r') as zip_ref:
                         # Ищем TTF‑файл в архиве
                        ttf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.ttf')]
                        if ttf_files:
                            # Извлекаем первый найденный TTF
                            ttf_filename = ttf_files[0]
                            extracted_path = save_path.parent / ttf_filename
                            zip_ref.extract(ttf_filename, save_path.parent)
                            print(f"Извлечён шрифт: {extracted_path}")
                    # Удаляем ZIP после извлечения
                            save_path.unlink()
                            return True
                        else:
                            print("В архиве не найдено TTF‑файлов")
                            save_path.unlink()
                            return False
                except Exception as e:
                    print(f"Ошибка при работе с ZIP‑архивом: {e}")
                    save_path.unlink()
                    return False

            # Дополнительная проверка — проверяем сигнатуру файла TTF (если это не ZIP)
            if not self._verify_ttf_signature(save_path):
                print("Ошибка: скачанный файл не является валидным TTF‑шрифтом")
                save_path.unlink()
                return False

            print(f"Шрифт успешно скачан: {save_path} (размер: {file_size} байт)")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка HTTP‑запроса: {e}")
            return False
        except Exception as e:
            print(f"Ошибка: неожиданная ошибка скачивания: {e}")
            return False


    def run(self, font_name=None):
        """
        Основной метод для запуска процесса.
        Если font_name указан — ищет конкретный шрифт, иначе — любой доступный.
        """
        print("Начинаем поиск шрифта на ofont.ru...")

        if font_name:
            download_link = self.find_font_by_name(font_name)
        else:
            download_link = self.find_any_font_link()

        if not download_link:
            print("Не удалось найти шрифт для скачивания")
            return False

        print(f"Найденная ссылка для скачивания: {download_link}")

        # Определяем имя файла
        if '.zip' in download_link.lower():
            filename = "Downloaded_Font.zip"
        else:
            filename = "Downloaded_Font.ttf"

        success = self.download_font(download_link, filename)
        return success


    def find_font_by_name(self, font_name):
        """Ищет конкретный шрифт по имени на сайте."""
        try:
            search_url = f"{self.base_url}/search/?q={urllib.parse.quote(font_name)}"
            print(f"Выполняем поиск: {font_name}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем карточки шрифтов
            font_cards = soup.find_all('div', class_='font-card')
            if not font_cards:
                font_cards = soup.find_all('a', class_='font-link')

            for card in font_cards:
                card_text = card.get_text().lower()
                if font_name.lower() in card_text:
                    link_tag = card.find('a')
                    if link_tag:
                        font_page = link_tag.get('href')
                        if font_page:
                            font_page_url = font_page if font_page.startswith('http') else f"{self.base_url}{font_page}"
                        # Переходим на страницу шрифта
                            font_response = self.session.get(font_page_url, timeout=10)
                            font_soup = BeautifulSoup(font_response.text, 'html.parser')

                # Ищем кнопку скачивания
                            download_btn = font_soup.find('a', {'class': re.compile(r'download|btn', re.IGNORECASE)})
                            if download_btn:
                                download_href = download_btn.get('href')
                                if download_href:
                                    potential_url = download_href if download_href.startswith('http') else f"{self.base_url}{download_href}"
                                    return self._encode_url(potential_url)

            print(f"Не удалось найти шрифт: {font_name}")
            return None
        except Exception as e:
            print(f"Ошибка при поиске шрифта {font_name}: {e}")
            return None

    # Запуск программы


if __name__ == "__main__":
    downloader = OfontDownloader("my_fonts")

    # Вариант 1: скачать любой шрифт
    print("\n=== ПОПЫТКА 1: Скачивание любого шрифта ===")
    success1 = downloader.run()

    # Вариант 2: скачать конкретный шрифт (например, Arial)
    print("\n=== ПОПЫТКА 2: Скачивание конкретного шрифта ===")
    success2 = downloader.run(font_name="Arial")

    if success1 or success2:
        print("Программа завершена успешно!")
    else:
        print("Произошла ошибка при скачивании шрифта")
