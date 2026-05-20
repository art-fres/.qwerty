import requests
import time
import threading
from datetime import datetime

DISK_URL = 'https://disk.yandex.ru/d/XxomzufLFsEapQ'
API_RESOURCES = 'https://cloud-api.yandex.net/v1/disk/public/resources'
API_DOWNLOAD = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'

cached_images: list[bytes] = []
_lock = threading.Lock()


def fetch_and_cache() -> list[bytes]:
    try:
        r = requests.get(API_RESOURCES, params={'public_key': DISK_URL, 'limit': 100}, timeout=15)
        r.raise_for_status()
        items = r.json().get('_embedded', {}).get('items', [])

        images = []
        for item in items:
            name = item.get('name', '').lower()
            if 'звонк' in name:
                continue
            if item.get('type') != 'file':
                continue
            path = item.get('path', '')
            dl = requests.get(API_DOWNLOAD, params={'public_key': DISK_URL, 'path': path}, timeout=15)
            if dl.status_code != 200:
                continue
            href = dl.json().get('href')
            if not href:
                continue
            img = requests.get(href, timeout=20)
            if img.status_code == 200:
                images.append(img.content)
                print(f"  Скачано: {item.get('name')} ({len(img.content)} байт)")

        print(f"Найдено и скачано картинок: {len(images)}")
        return images

    except Exception as e:
        print(f"Ошибка при загрузке картинок: {e}")
        return []


def reload_parsing_data():
    global cached_images
    try:
        new_images = fetch_and_cache()
        with _lock:
            cached_images = new_images
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Кэш обновлён. Картинок: {len(new_images)}")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Ошибка обновления: {e}")
        return False


def run_parsing_at_8am():
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            try:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Время 8:00 - обновляю данные!")
                reload_parsing_data()
                time.sleep(120)
            except Exception as e:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Ошибка: {e}")
        time.sleep(60)


print("🔄 Загружаю расписание при старте...")
cached_images = fetch_and_cache()
print(f"✅ Готово. Картинок в кэше: {len(cached_images)}")

scheduler_thread = threading.Thread(target=run_parsing_at_8am, daemon=True)
scheduler_thread.start()
print("✅ Планировщик запущен. Следующее обновление в 8:00")
