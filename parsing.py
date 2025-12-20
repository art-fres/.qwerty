import requests
import time
import random
import re
import urllib.parse
from typing import List, Optional
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from config import z, z2
class YandexDiskScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]

        # Сессия для повторного использования соединений
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def get_enhanced_headers(self) -> dict:
        """Быстрая генерация заголовков без кеширования"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Referer': 'https://yandex.ru/',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
        }

    def simulate_human_behavior(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Сокращенные задержки"""
        time.sleep(random.uniform(min_delay, max_delay))

    def make_stealth_request(self, url: str, max_retries: int = 2) -> Optional[requests.Response]:
        """Оптимизированный запрос"""
        for attempt in range(max_retries):
            # Сокращаем задержку перед запросом
            if attempt > 0:
                self.simulate_human_behavior(1.0, 8.0)

            # Случайные параметры для обхода кеширования
            params = {
                '_': int(time.time() * 1000),
                'rand': random.randint(100, 999)
            }

            headers = self.get_enhanced_headers()

            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=10,  # Уменьшаем таймаут
                    allow_redirects=True,
                    verify=True
                )

                if response.status_code == 200:
                    return response
                elif response.status_code in [403, 429]:
                    print(f"Защита {response.status_code}, ожидание...")
                    time.sleep(random.uniform(5, 10))
                else:
                    time.sleep(random.uniform(2, 5))

            except requests.exceptions.RequestException as e:
                print(f"Попытка {attempt + 1} ошибка: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))

        return None

    def extract_links_from_text(self, text: str) -> List[str]:
        """Быстрое извлечение ссылок с компилированным regex"""
        # Компилируем regex заранее для производительности
        patterns = [
            re.compile(r'https?://downloader\.disk\.yandex\.ru/preview/[a-f0-9]+/[a-f0-9]+/[^\s"\']*?\?[^\s"\']*', re.I),
            re.compile(r'https?://[^\s"\']*?\.yandex\.[^\s"\']*?/disk/[^\s"\']*', re.I),
            re.compile(r'https?://[^\s"\']*?\.yandex\.[^\s"\']*?/preview/[^\s"\']*', re.I),
        ]

        links = []
        for pattern in patterns:
            links.extend(pattern.findall(text))

        # Убираем дубликаты быстрее через set
        return list(set(links))

    def get_yandex_disk_links(self, url: str) -> List[str]:
        """Оптимизированная основная функция"""
        start_time = time.time()

        response = self.make_stealth_request(url)

        if not response or response.status_code != 200:
            print("Не удалось получить ответ от сервера")
            return []

        # Быстрое извлечение ссылок
        links = self.extract_links_from_text(response.text)

        if not links:
            print("Не найдено ссылок")
            return []

        # Фильтрация и обработка
        fixed_links = [link.replace('\\u0026', '&') for link in links]

        # Фильтруем только XXXL ссылки
        xxxl_links = [link for link in fixed_links if "XXXL" in link.upper() and z not in link and z2 not in link]

        if not xxxl_links:
            print("Не найдено ссылок с size=XXXL")
            return []

        # Убираем дубликаты (если есть)
        unique_links = list(set(xxxl_links))

        # Если нужно оставить только самую короткую ссылку


        print(f"Найдено ссылок: {len(unique_links)} за {time.time() - start_time:.2f} сек")
        return unique_links

    def get_yandex_disk_links_batch(self, urls: List[str], max_workers: int = 3) -> dict:
        """Пакетная обработка нескольких URL"""
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.get_yandex_disk_links, url): url for url in urls}

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = []
                    print(f"Ошибка для {url}: {e}")

        return results


def f(url: str) -> str:
    """Простая замена без лишних вызовов"""
    return url.replace('\\u0026', '&')


scraper = YandexDiskScraper()
test_url = 'https://disk.yandex.ru/d/XxomzufLFsEapQ'
result = scraper.get_yandex_disk_links(test_url)