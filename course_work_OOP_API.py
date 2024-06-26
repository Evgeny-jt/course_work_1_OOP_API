import requests
import json
from pprint import pprint


class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.199'
        }

    def get_info(self):
        params = self.get_common_params()
        params.update({'user_id': self.user_id})

        response = requests.get(f'{self.API_BASE_URL}method/users.get', params=params)
        return response.json()

    def photo(self):
        params = self.get_common_params()
        params.update({'user_id': self.user_id})
        params.update({'album_id': 'wall'})
        params.update({'extended': 1})

        response = requests.get(f'{self.API_BASE_URL}method/photos.get', params=params)
        date_photos = response.json()['response']['items']
        photos = {}
        url_photo = ''
        like_photo = ''

        for i, date in enumerate(date_photos):
            for key, value in date.items():
                print(key,value)
                if key == 'date':
                    date_photo = date_photos[i][key]
                    photos[date_photo] = [date_photo]
                if key == 'sizes':
                    for all_photo in date_photos[i][key]:
                        for key_photo_w, value_photo_w in all_photo.items():
                            if all_photo[key_photo_w] == 'w':
                                url_photo = all_photo['url']
                if key == 'likes':
                    like_photo = date_photos[i][key]['count']
            photos[date_photo] = {'url': url_photo, 'likes': like_photo}
        return photos

    def save_file_json(self):
        with open('files/url_photo_VK.json', 'w', encoding='utf-8') as f:
            json.dump(vk_client.photo(), f, ensure_ascii=False, indent=2)
        print('Ссылки фотографий сохранены в url_photo_VK.json')


class YandexDisk:

    def __init__(self, token, name_folder='Photo_VK'):
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.token = {'Authorization': token}
        self.params_init = {'path': name_folder}
        print(f'Создаем папку {name_folder} на ЯНДЕКС ДИСКЕ')
        response = requests.put(self.url, params=self.params_init, headers=self.token)
        if response.status_code == 201:
            print(f'Папка {name_folder} создана на ЯНДЕКС ДИСКЕ')
        elif response.status_code == 409:
            print(response.json()['message'])

    def save_photo(self, url_photo, name_file):
        self.params = {'path': f'{self.params_init['path']}/{name_file}'}
        response_photo = requests.get(url_photo)
        response = requests.get(url='https://cloud-api.yandex.net/v1/disk/resources/upload',
                                params=self.params,
                                headers=self.token)
        url_for_upload = response.json()['href']
        requests.put(url_for_upload, files={'file': response_photo.content})





if __name__ == '__main__':
    print('Для резервного копирования фотографий с социальной сети В КОНТАКТЕ, на ЯНДЕКС ДИСК необходимо: ')
    TOKEN_VK = input('ввести токен В КОНТАКТЕ: ')
    TOKEN_YANDEX = input('ввести токен ЯНДЕКС ДИСКа: ')
    # TOKEN_VK = 'vk1.a.j1JuaC4V3zSF2y1bE4vsK-o1Y_kvnqeRLvMBOjLq8vsStTb6ZcKxZnBwqBtTKbN4ONhqB9yOU8vS-pGsdCuxrnSbqWvrUqEuV9WMO5qLLtinEQ44j97qs43ROdrJvMZFOixsdtv-yta1q-W0I2yk3xBSXS1pM0KjtaLVoXhk9Yqjb7eaIId4sia-FIqcdBTy'
    # TOKEN_YANDEX = 'y0_AgAAAAAMTsynAADLWwAAAAEFACEgAADDPPEo4XBLRIDdPGApqHIbErhZcQ'
    vk_client = VKAPIClient(token=TOKEN_VK, user_id=795654478)
    info_user = vk_client.get_info()
    photo_wall = vk_client.photo()
    vk_client.save_file_json()

    save_yd = YandexDisk(token=TOKEN_YANDEX, name_folder='photo_save')
    with open('files/url_photo_VK.json', 'r', encoding='utf-8') as f:
        json_date = json.load(f)
    likes = {}
    for name, date in json_date.items():
        if len(likes) != 0:
            if date['likes'] in likes:
                likes[date['likes']] += 1
            else:
                likes[date['likes']] = 0
        else:
            likes[date['likes']] = 0

    print('Подождите пока фото скопируются на ЯНДЕКС ДИСК')
    quantity_photo = 0
    for name, value in json_date.items():
        if likes[value['likes']] > 0:
            name_file = f'{value['likes']} - {name}'
        else:
            name_file = value['likes']
        url = value['url']
        sevef = save_yd.save_photo(url_photo=url, name_file=name_file)
        quantity_photo += 1
    print(f'{quantity_photo} фотографий сохранено на диск')
