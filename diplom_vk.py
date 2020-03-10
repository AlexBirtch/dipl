import json
import os
import requests
import inspect
from time import sleep

token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'

def get_user_input():
    user_input = input('Введите id пользователья: (прим. 301364322): ')
    return user_input

class UserVk:

    TOKEN = token
    error_user = []

    def __init__(self, user_id):
        self.user_id = user_id
        self.dirname = os.path.dirname(os.path.abspath(inspect.stack()[-1][1]))

    def response_param(self, id, share):
        return dict(v='5.103', access_token=UserVk.TOKEN, user_id=id, extended=share)

    def get_friends(self):
        params = self.response_param(self.user_id, 0)
        response = requests.get(
            'https://api.vk.com/method/friends.get',
            params)
        return response.json()

    def user_groups(self, id_num):
        params = self.response_param(id_num, 0)
        response = requests.get(
            'https://api.vk.com/method/groups.get',
            params)
        return response.json()

    def summary_groups(self):
        result_user = self.get_friends()
        friends = self.transform_friends(result_user)
        groups_dict = set()
        for k, id_num in enumerate(friends):
            print(f'Обрабатываем {k} из {len(friends)}')
            json_data = self.user_groups(id_num)
            try:
                for i in range(len(json_data['response']['items'])):
                    res = json_data['response']['items'][i]
                    groups_dict.add(res)
            except KeyError:
                self.error_user.append(id_num)
                sleep(0.5)
        return groups_dict

    def compare_groups(self):
        friend_groups = self.summary_groups()
        sleep(.5)
        res_my_groups = self.user_groups(self.user_id)
        my_groups = self.transform_friends(res_my_groups)
        total = set(my_groups).difference(set(friend_groups))
        return total

    def get_description_group(self, id_group):
        params_group = {
            'v': '5.103',
            'access_token': UserVk.TOKEN,
            'group_id': id_group,
            'fields': 'members_count,name,id'
        }
        response = requests.get(
            'https://api.vk.com/method/groups.getById',
            params_group)
        sleep(.5)
        return response.json()

    def info_groups_res(self):
        list_groups = self.compare_groups()
        list_result_info = []
        for id_group in list_groups:
            json_data = self.get_description_group(id_group)
            dict_res = {}
            for i in range(len(json_data['response'])):
                for key, value in json_data['response'][i].items():
                    if key == 'id':
                        dict_res[key] = value
                    if key == 'name':
                        dict_res[key] = value
                    if key == 'members_count':
                        dict_res[key] = value
            list_result_info.append(dict_res)
            sleep(.5)
        filename = self.convert_to_json(list_result_info)
        return filename

    def convert_to_json(self, list_json):
        data = json.dumps(list_json).encode('utf8')
        json_data = json.loads(data)
        with open('groups.json', 'w', encoding='utf8') as outfile:
            json.dump(json_data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
        filename = os.path.join(self.dirname, 'groups.json')
        return filename

    def transform_friends(self, json_data):
        friends_dict = set()
        for i in range(len(json_data['response']['items'])):
            string = json_data['response']['items'][i]
            friends_dict.add(string)
        return friends_dict

    def __str__(self):
        data = json.dumps(self.error_user)
        json_data = json.loads(data)
        with open('groups_error.json', 'w', encoding='utf8') as outfile:
            json.dump(json_data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
        filename = os.path.join(self.dirname, 'groups_error.json')
        return f'Запросы для групп к которым возвращена ошибка выгружены в файл: {filename}'

if __name__ == "__main__":
    try:
        user = UserVk(get_user_input())
        print(f'результат в файле {user.info_groups_res()}')
        print(user)
        print(user.transform_friends(user.get_friends()))
    except IndexError:
        pass