import requests
import time
from bs4 import BeautifulSoup
import random
import re
import urllib.parse
from config import z

def get_enhanced_headers():
    """Генерирует улучшенные заголовки для обхода защиты"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]

    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://yandex.ru/',
        'DNT': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

def simulate_human_behavior():
    """Имитирует человеческое поведение"""
    time.sleep(random.uniform(3, 8))
    if random.random() > 0.7:
        time.sleep(random.uniform(0.5, 1.5))

def make_stealth_request(url, max_retries=3):
    """Выполняет скрытный запрос с повторными попытками"""
    for attempt in range(max_retries):
        simulate_human_behavior()

        headers = get_enhanced_headers()
        cookies = {'yandexuid': str(random.randint(1000000000, 9999999999))}

        try:
            if '?' in url:
                modified_url = f"{url}&_={int(time.time())}{random.randint(100,999)}"
            else:
                modified_url = f"{url}?_{int(time.time())}{random.randint(100,999)}"

            response = requests.get(
                modified_url,
                headers=headers,
                cookies=cookies,
                timeout=15,
                allow_redirects=True,
                verify=True
            )

            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print("Обнаружена защита 403, жду...")
                time.sleep(random.uniform(10, 20))
            else:
                time.sleep(random.uniform(5, 10))

        except Exception as e:
            print(f"Ошибка при попытке {attempt + 1}: {e}")
            time.sleep(random.uniform(8, 15))

    return None

def extract_links_from_text(text):
    """Извлекает ссылки из текста"""
    patterns = [
        r'https?://downloader\.disk\.yandex\.ru/preview/[a-f0-9]+/[a-f0-9]+/[^\s"\']*?\?[^\s"\']*',
        r'https?://[^\s"\']*?\.yandex\.[^\s"\']*?/disk/[^\s"\']*',
        r'https?://[^\s"\']*?\.yandex\.[^\s"\']*?/preview/[^\s"\']*',
    ]

    links = []

    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        links.extend(found)

    return list(set(links))

def f(url):
    return url.replace('\\u0026', '&')

def get_yandex_disk_links(url):
    response = make_stealth_request(url)

    if response and response.status_code == 200:
        links = extract_links_from_text(response.text)

        fixed_links = []
        for link in links:
            fixed_link = f(link)
            fixed_links.append(fixed_link)

        filtered_links = []
        for link in fixed_links:
            if "XXXL" in link and link != z :
                filtered_links.append(link)

        if filtered_links:
            filtered_links.sort(key=len)
            if len(filtered_links) > 1:
                filtered_links.pop(-1)
            print(f"Найдено ссылок: {len(filtered_links)}")
            return filtered_links
        else:
            print("Не найдено ссылок с size=XXXL")
            return []
    else:
        print("Не удалось получить ответ от сервера")
        return []


if __name__ == "__main__":
    test_url = 'https://disk.yandex.ru/d/XxomzufLFsEapQ'
    result = get_yandex_disk_links(test_url)
    print("Результат:", result)
