import os
import re
import csv
import json
import requests
import time
from tqdm import tqdm
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Configuration for Iranian Pottery Dataset ===
CONFIG = {
    "dataset_path": "./iran_pottery_dataset",
    "timeout": 25,
    "retries": 4,
    "max_images": 200,  # Maximum total number of images
    "historical_periods": {
        "pre_islamic": [
            "Silk", "Elam", "Achaemenid", "Parthian", "Sassanian", 
            "Chogha Zanbil", "Tappeh Sialk", "Haft Tepe",
            "Kuh-e Khwaja", "Arg-e Bam", "Persepolis", "Ancient Iran",
            "Zagros", "Luristan"
        ],
        "islamic": [
            "Islamic", "Ilkhanid", "Timurid", "Safavid", "Qajar",
            "Ottoman", "Seljuk", "Mongol", "Abbasid", "Umayyad"
        ]
    },
    "metadata_fields": [
        'objectID', 'title', 'culture', 'period', 'objectDate', 
        'objectName', 'classification', 'medium', 'dimensions',
        'creditLine', 'country', 'region', 'tags', 'isPublicDomain',
        'primaryImage', 'era_classification', 'historical_period',
        'local_path', 'source'
    ],
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
}

# === Helper Functions ===
def get_random_user_agent():
    """Return a random User-Agent string."""
    return random.choice(CONFIG['user_agents'])


def normalize_text(text):
    """Clean and normalize text fields."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:500]


def detect_historical_period(obj_data):
    """
    Determine the historical period (pre-Islamic or Islamic) and sub-period
    based on title, culture, period, and objectDate fields.
    """
    title = obj_data.get('title', '').lower()
    culture = obj_data.get('culture', '').lower()
    period = obj_data.get('period', '').lower()
    object_date = obj_data.get('objectDate', '').lower()

    # Check pre-Islamic sub-period keywords
    for period_name in CONFIG['historical_periods']['pre_islamic']:
        if period_name.lower() in title or period_name.lower() in culture or period_name.lower() in period or period_name.lower() in object_date:
            return "pre_islamic", period_name
    # Check Islamic sub-period keywords
    for period_name in CONFIG['historical_periods']['islamic']:
        if period_name.lower() in title or period_name.lower() in culture or period_name.lower() in period or period_name.lower() in object_date:
            return "islamic", period_name
    # Fallback by date indicators
    if any(x in object_date for x in ["bc", "b.c.", "before christ"]):
        return "pre_islamic", "Ancient Iran"
    if any(x in object_date for x in ["islamic", "ad", "a.d.", "hijri", "ah"]):
        return "islamic", "Islamic Period"
    return "unknown", "Unknown"


def download_image(url, filepath):
    """Download an image from URL with retry logic and minimum size check."""
    headers = {'User-Agent': get_random_user_agent()}
    for _ in range(CONFIG['retries']):
        try:
            resp = requests.get(url, headers=headers, timeout=CONFIG['timeout'], stream=True)
            resp.raise_for_status()
            # Ensure image is larger than 10KB
            if len(resp.content) < 10 * 1024:
                continue
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return True
        except Exception:
            time.sleep(2)
    return False



def download_iran_pottery():
    """
    1. Collect object IDs via MET API search for various queries.
    2. Group IDs by detected sub-period and sample evenly up to max_images.
    3. Download images into structured folders and save metadata.
    Now fully multithreaded for speed.
    """
    os.makedirs(CONFIG['dataset_path'], exist_ok=True)
    image_dir = os.path.join(CONFIG['dataset_path'], 'images')
    os.makedirs(image_dir, exist_ok=True)

    search_queries = [
        "Persian pottery", "Iranian ceramics", "Ancient Iranian pottery",
        "Islamic pottery Iran", "Pre-Islamic ceramics Iran",
        "Sialk pottery", "Elam pottery", "Achaemenid ceramics",
        "Parthian pottery", "Sasanian ceramics", "Chogha Zanbil pottery",
        "Haft Tepe ceramics", "Kuh-e Khwaja pottery", "Arg-e Bam ceramics",
        "Safavid pottery", "Qajar ceramics"
    ]

    # Step 1: Collect all object IDs
    all_ids = set()
    print("🔍 Performing initial search...")
    for q in search_queries:
        try:
            params = {'q': q, 'hasImages': 'true'}
            r = requests.get(
                'https://collectionapi.metmuseum.org/public/collection/v1/search',
                params=params,
                headers={'User-Agent': get_random_user_agent()},
                timeout=20
            )
            r.raise_for_status()
            data = r.json()
            ids = data.get('objectIDs') or []
            all_ids.update(ids)
        except Exception:
            continue
        time.sleep(1)  # polite delay to prevent blocking

    # Step 2: Group and sample objects evenly using multithreading
    groups = {}
    print("👥 Grouping object IDs by sub-period...")

    def fetch_and_group(obj_id):
        try:
            obj_data = requests.get(
                f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}',
                headers={'User-Agent': get_random_user_agent()},
                timeout=10
            ).json()
            era, pname = detect_historical_period(obj_data)
            return pname, obj_id
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(fetch_and_group, obj_id): obj_id for obj_id in all_ids}
        for future in tqdm(as_completed(futures), total=len(futures), desc='Initial grouping'):
            result = future.result()
            if result:
                pname, obj_id = result
                groups.setdefault(pname, []).append(obj_id)

    min_count = min(len(ids) for ids in groups.values() if ids)
    target_per_group = max(1, min(min_count, CONFIG['max_images'] // len(groups)))

    sampled = []
    for pname, ids in groups.items():
        if not ids:
            continue
        if len(ids) <= target_per_group:
            sampled.extend(ids)
        else:
            sampled.extend(random.sample(ids, target_per_group))

    sampled = sampled[:CONFIG['max_images']]
    print(f"🎯 Ready to download {len(sampled)} images")

    # Step 3: Download images and save metadata using multithreading
    metadata = []

    def process_and_download(obj_id):
        try:
            return process_pottery_object(obj_id, image_dir)
        except Exception as e:
            print(f"❌ Error processing {obj_id}: {e}")
            return None

    print("📥 Downloading images and metadata...")
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(process_and_download, obj_id): obj_id for obj_id in sampled}
        for future in tqdm(as_completed(futures), total=len(futures), desc='Downloading images'):
            result = future.result()
            if result:
                metadata.append(result)

    save_metadata(metadata)
    print(f"✅ Completed: downloaded {len(metadata)} images")

def process_pottery_object(obj_id, image_dir):
    """
    Fetch full object data, determine period, create folder,
    download image, and return metadata record.
    """
    url = f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}'
    data = requests.get(url, headers={'User-Agent': get_random_user_agent()}, timeout=25).json()

    if not data.get('primaryImage'):
        raise ValueError('No primary image available')

    era, pname = detect_historical_period(data)
    # Create sub-folder for period
    folder = os.path.join(image_dir, era, pname.replace(' ', '_'))
    os.makedirs(folder, exist_ok=True)

    # Download image
    img_name = f"{obj_id}.jpg"
    img_path = os.path.join(folder, img_name)
    if not download_image(data['primaryImage'], img_path):
        raise ConnectionError('Image download failed')

    # Return metadata record
    return {
        'objectID': obj_id,
        'title': normalize_text(data.get('title')),
        'culture': normalize_text(data.get('culture')),
        'period': normalize_text(data.get('period')),
        'objectDate': normalize_text(data.get('objectDate')),
        'objectName': normalize_text(data.get('objectName')),
        'classification': normalize_text(data.get('classification')),
        'medium': normalize_text(data.get('medium')),
        'dimensions': normalize_text(data.get('dimensions')),
        'creditLine': normalize_text(data.get('creditLine')),
        'country': normalize_text(data.get('country')),
        'region': normalize_text(data.get('region')),
        'tags': ', '.join(data.get('tags') or []),
        'isPublicDomain': data.get('isPublicDomain', False),
        'primaryImage': data.get('primaryImage'),
        'era_classification': era,
        'historical_period': pname,
        'local_path': img_path,
        'source': 'MET'
    }


def save_metadata(metadata):
    os.makedirs(CONFIG['dataset_path'], exist_ok=True)
    path_json = os.path.join(CONFIG['dataset_path'], 'iran_pottery_metadata.json')
    with open(path_json, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    if metadata:
        path_csv = os.path.join(CONFIG['dataset_path'], 'iran_pottery_metadata.csv')
        with open(path_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CONFIG['metadata_fields'])
            writer.writeheader()
            writer.writerows(metadata)

if __name__ == "__main__":
    download_iran_pottery()
