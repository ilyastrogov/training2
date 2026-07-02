import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
import urllib.parse

class MonotypeCorsivaDownloader:
    def __init__(self, download_folder="downloaded_fonts"):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.base_url = "https://ofont.ru"
        self.search_url = 'https://ofont.ru/view/1537'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _encode_url(self, url):
        """Кодирует URL, заменяя кириллические символы на percent‑encoding."""
        parsed = urllib.parse.urlparse(url)
        encoded_path = urllib.parse.quote(parsed.path.encode('utf-8'))
        # print(encoded_path)
        encoded_query = urllib.parse.quote(parsed.query.encode('utf-8'))
        # print(encoded_query)
        encoded_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            encoded_path,
            parsed.params,
            encoded_query,
            parsed.fragment
        ))
        # print(encoded_url)
        return encoded_path

    def find_download_link(self):
        """Ищет реальную ссылку для скачивания шрифта."""
        try:
            print(f"Загружаем страницу: {self.search_url}")
            response = self.session.get(self.search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            print('soup', soup)
            # Ищем прямые ссылки на .ttf файлы
            ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
            for link in ttf_links:
                href = link.get('href')
                if href and not href.startswith('#'):
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = href
            # Кодируем URL перед возвратом
                    print(full_url)
                    return self._encode_url(full_url)

            # Вариант 2: ищем кнопки с атрибутом download
            # Способ 1: find_all с class_
            download_links1 = soup.find_all('a', class_='btn')
            print('1',download_links1 )
            # Способ 2: CSS-селекторы
            download_links2 = soup.select('a.btn')
            print('2', download_links2)
            # Способ 3: через attrs
            download_links3 = soup.find_all('a', attrs={'class': 'btn'})
            print('3',download_links3)
            for link in download_links1:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        return f"{self.base_url}{href}"
                return href

            # Если прямых ссылок нет, ищем кнопки модальных окон
            modal_buttons = soup.find_all('a', {'/index.php?act=download&font_id=1537': 'modal'})
            print(modal_buttons)
            for button in modal_buttons:
                font_id = button.get('data-fn')
                print(font_id)
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

    def download_font(self, link, filename="Monotype_Corsiva.ttf"):
        """Скачивает шрифт по найденной ссылке с проверкой содержимого."""
        try:
            if not link or link.startswith('#') or link.startswith('javascript:'):
                print("Недопустимая ссылка для скачивания")
                return False

            print(f"Исходный URL: {link}")
            encoded_link = self._encode_url(link)
            print(f"Закодированный URL: {encoded_link}")

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
