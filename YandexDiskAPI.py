import json
import requests
import time
from urllib.parse import quote
from tqdm import tqdm
import datetime


def get_photos():
    url_vk = (f'https://api.vk.com/method/photos.get'
              f'?owner_id={user_id}'
              f'&album_id=profile'
              f'&extended=1&'
              f'count={count}'
              f'&access_token={token_vk}'
              f'&v=5.199')
    response_vk = requests.post(url_vk).json()
    if 'error' in response_vk:
        if response_vk['error']['error_code'] == 30:
            return 'Can not upload photos :( This profile is private'
        else:
            return 'Can not upload photos :('
    photos = []
    names = []
    for photo in response_vk['response']['items']:
        photos.append({'file_name': photo['likes']['count'],
                       'size': photo['sizes'][-1]['type'],
                       'url': photo['sizes'][-1]['url'],
                       'date': photo['date']})
    for i in range(len(photos)):
        names.append(photos[i]['file_name'])
    for name in names:
        if names.count(name) > 1:
            photos[names.index(name)]['file_name'] = \
                (f'{photos[names.index(name)]["file_name"]}'
                 f'_{datetime.datetime.fromtimestamp(photos[names.index(name)]["date"])}')
    return photos

def new_folder():
    url_ya = f'https://cloud-api.yandex.net/v1/disk/'
    headers = {'Authorization': f'OAuth {token_ya}'}
    response = requests.put(f'{url_ya}resources?path=PhotosFromVK', headers=headers)
    return response

def get_link():
    url_ya = f'https://cloud-api.yandex.net/v1/disk/'
    headers = {'Authorization': f'OAuth {token_ya}'}
    response = requests.get(url_ya, headers=headers).json()
    return f'https://disk.yandex.ru/{response["user"]["login"]}'

def save_photos_to_ya():
    url_ya = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    photos = get_photos()
    new_folder()
    res = []
    headers = {'Authorization': f'OAuth {token_ya}'}
    if 'photos' in photos:
        print(photos)
        return
    for photo in photos:
        file_name = str(photo['file_name'])+'.jpg'
        file_url = quote(photo['url'])
        file_size = str(photo['size'])
        url_upload = (f'{url_ya}'
                      f'?url={file_url}'
                      f'&path=disk%3A%2FPhotosFromVK%2F{file_name}')
        requests.post(url_upload, headers=headers)
        for _ in tqdm(range(100)):
            time.sleep(0.02)
        res.append({"file_name": file_name, "size": file_size})
    print(f'Yandex-disk link: {get_link()}')
    return res


count = 5
user_id = input('1. VK user-ID:')
token_ya = input('2. Yandex-Disk token:')
token_vk = input('3. VK token:')

result = save_photos_to_ya()

with open('photos_info.json', 'w', encoding='utf-8') as file:
    json.dump(result, file, ensure_ascii=False, indent=4)

