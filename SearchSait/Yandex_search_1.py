import time
import random
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re

class AdvancedFontDownloader:
    def __init__(self, download_folder="downloaded_fonts", proxies=None):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.proxies = proxies or []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        # Обновляем User-Agent случайным образом
        self._update_user_agent()
        # Список сайтов для поиска
        self.sites = [
            "ofont.ru",
            "fonts-online.ru",
            "fontstorage.com",
            "allfonts.net"
        ]

    def _update_user_agent(self):
        """Обновляет User-Agent для сессии."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': user_agent})

    def search_via_yandex(self, query):
        """Ищет через Яндекс и возвращает список URL из результатов поиска."""
        print(f"Выполняем поиск в Яндексе: {query}")

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Edge(options=options)

        try:
            # Открываем Яндекс
            driver.get("https://yandex.ru/search/")

            # Ждём и вводим запрос
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.submit()

            # Умное ожидание результатов
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".serp-item"))
            )

            # Улучшенные селекторы для поиска ссылок
            selectors = [
                ".serp-item a.link",
                ".organic__url",
                "a[href*='yandex.ru']",
                ".path__item"
            ]

            urls = []
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and href.startswith("http") and "yandex.ru" not in href:
                            urls.append(href)
                except Exception:
                    continue

            # Убираем дубликаты
            urls = list(set(urls))

            print(f"Найдено {len(urls)} уникальных URL из поиска")
            return urls

        except TimeoutException:
            print("Таймаут ожидания результатов поиска")
            driver.save_screenshot("yandex_search_timeout.png")
            return []
        except Exception as e:
            print(f"Критическая ошибка при поиске в Яндексе: {e}")
            driver.save_screenshot("yandex_search_error.png")
            return []
        finally:
            driver.quit()

    def _make_absolute_url(self, relative_url, base_url):
        """Создаёт абсолютный URL из относительного."""
        if not relative_url:
            return None
        if relative_url.startswith('http'):
            return relative_url
        elif relative_url.startswith('/'):
            from urllib.parse import urlparse
            base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
            return f"{base_domain}{relative_url}"
        else:
            if not base_url.endswith('/'):
                base_url += '/'
            return f"{base_url}{relative_url}"

    def _retry_with_delay(self, func, *args, max_attempts=3, **kwargs):
        """Выполняет функцию с повторными попытками и экспоненциальной задержкой."""
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except (TimeoutException, ConnectionError) as e:
                if attempt == max_attempts - 1:
                    raise e
                delay = 2 ** attempt  # 2, 4, 8 секунд
                print(f"Попытка {attempt + 1} не удалась. Повторная попытка через {delay} сек...")
                time.sleep(delay)
                # Обновляем User-Agent и прокси при повторной попытке
                self._update_user_agent()
                if self.proxies:
                    self.session.proxies.update({'http': random.choice(self.proxies),
                                                   'https': random.choice(self.proxies)})
        return None

    def find_download_links_on_page(self, url):
        """Находит ссылки для скачивания на указанной странице, используя Selenium для динамического контента."""
        def _find_links():
            # Сначала пробуем requests (для статических страниц)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем прямые ссылки на TTF
            ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
            direct_links = [link.get('href') for link in ttf_links if link.get('href')]

            # Если не нашли, используем Selenium для динамического контента
            if not direct_links:
                print(f"Попытка использования Selenium для {url} (динамический контент)")
                options = Options()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                driver = webdriver.Edge(options=options)

                try:
                    driver.get(url)
                    # Ждём появления кнопки скачивания
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.ttf'], button, .download-btn"))
                    )

                    # Получаем обновлённый HTML после выполнения JavaScript
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    # Ищем ссылки после выполнения JS
                    ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
                    direct_links = [link.get('href') for link in ttf_links if link.get('href')]

                    # Дополнительно ищем кнопки скачивания
                    download_buttons = soup.find_all(
                        ['button', 'a'],
                        class_=re.compile(r'download|скачать', re.IGNORECASE)
                    )

                    for button in download_buttons:
                        href = button.get('href')
                        onclick = button.get('onclick')

                        if href:
                            full_url = self._make_absolute_url(href, url)
                            print(f"Кнопка скачивания: {full_url}")
                            direct_links.append(full_url)

                        elif onclick and 'download' in onclick.lower():
                            # Иногда ссылка генерируется через JavaScript
                            match = re.search(r"['\"]([^'\"]+)", onclick)
                            if match:
                                js_url = match.group(1)
                                full_url = self._make_absolute_url(js_url, url)
                                print(f"Ссылка из JavaScript: {full_url}")
                                direct_links.append(full_url)

                    return direct_links

                finally:
                    driver.quit()

            # Преобразуем относительные URL в абсолютные

            absolute_links = []
            for link in direct_links:
                absolute_url = self._make_absolute_url(link, url)
                if absolute_url:
                    absolute_links.append(absolute_url)

            print(f"На странице {url} найдено {len(absolute_links)} ссылок для скачивания")
            return absolute_links

            # Выполняем поиск ссылок с повторными попытками


        try:
            direct_links = self._retry_with_delay(_find_links)
            if not direct_links:
                print(f"Не удалось найти ссылки для скачивания на {url}")
                return []

            # Преобразуем относительные URL в абсолютные
            absolute_links = []
            for link in direct_links:
                absolute_url = self._make_absolute_url(link, url)
                if absolute_url:
                    absolute_links.append(absolute_url)

            print(f"На странице {url} найдено {len(absolute_links)} ссылок для скачивания")
            return absolute_links
        except Exception as e:
            print(f"Ошибка при анализе страницы {url}: {e}")
            return []


    def download_font(self, link, filename):
        """Скачивает шрифт по найденной ссылке."""

        def _download(link, filename):
            try:
                if not link or link.startswith('#') or link.startswith('javascript:'):
                    print(f"Недопустимая ссылка: {link}")
                    return False

                # Для GitHub используем специальный подход
                if 'github.com' in link:
                    link = link.replace('/blob/', '/raw/')

                response = self.session.get(
                    link,
                    stream=True,
                    timeout=30,
                    allow_redirects=True
                )
                response.raise_for_status()

                save_path = self.download_folder / filename

                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                file_size = save_path.stat().st_size
                if file_size == 0:
                    print(f"Ошибка: файл {filename} имеет нулевой размер")
                    save_path.unlink()
                    return False

                print(f"Шрифт успешно скачан: {save_path} (размер: {file_size} байт)")
                return True
            except requests.exceptions.ConnectionError as e:
                print(f"Ошибка подключения при скачивании {link}: {e}")
                raise e
            except Exception as e:
                print(f"Ошибка скачивания {link}: {e}")
                raise e

        # Выполняем скачивание с повторными попытками
        try:
            return self._retry_with_delay(_download, link, filename)
        except Exception:
            return False


    def run(self, font_name="Monotype Corsiva"):
        """Основной метод для запуска процесса."""
        query = f"скачать {font_name} ttf"
        print(f"Начинаем поиск: {query}")

        # Шаг 1: поиск через Яндекс
        search_urls = self.search_via_yandex(query)
        if not search_urls:
            print("Не удалось получить результаты поиска")
            return False

        downloaded_count = 0
        max_downloads = 4  # Скачиваем максимум с 4 сайтов

        for site_url in search_urls:
            if downloaded_count >= max_downloads:
                break

            print(f"\nАнализируем сайт: {site_url}")

            # Шаг 2: находим ссылки для скачивания на странице
            download_links = self.find_download_links_on_page(site_url)
            for link in download_links:
                if downloaded_count >= max_downloads:
                    break

                # Формируем имя файла
                filename = f"{font_name.replace(' ', '_')}_{downloaded_count + 1}.ttf"

                # Шаг 3: скачиваем шрифт
                success = self.download_font(link, filename)
                if success:
                    downloaded_count += 1

        print(f"\nЗавершено: скачано {downloaded_count} шрифтов из {max_downloads} возможных")
        return downloaded_count > 0


# Запуск программы
if __name__ == "__main__":
    # Можно задать прокси, если нужно: proxies = ["http://proxy1:port", "http://proxy2:port"]
    downloader = AdvancedFontDownloader("my_fonts", proxies=[])
    success = downloader.run("Brush Script")
    if success:
        print("Программа завершена успешно!")
    else:
        print("Произошла ошибка при скачивании шрифтов")
