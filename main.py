import json
import os
import time
import requests

from config import LANGUAGE, URL, VK_METHOD_VERSION, VK_TOKEN
from graph_visualizer import visualize_friends_graph

class UserFriendsFetcher:
    def __init__(self, token, version=VK_METHOD_VERSION, lang=LANGUAGE):
        self.token = token
        self.version = version
        self.lang = lang
        self.api_url_friends = f'{URL}/friends.get'
        self.api_url_users = f'{URL}/users.get'
    
    def load_user_ids(self, filepath):
        """Загрузка id пользователей из файла

        Args:

            filepath str: Пуь до файла group_ids.json

        Returns:
            List: user_ids
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                user_ids = json.load(file)
            return user_ids
        except FileNotFoundError:
            print(f"Файл {filepath} не найден.")
            return []
        except json.JSONDecodeError:
            print(f"Ошибка при чтении файла {filepath}. Убедитесь, что это правильный JSON.")
            return []

    def fetch_user_name(self, user_id):
        """Получение имя и фамилию пользователя по ID

        Args:
            user_id (int): ID пользователя

        Returns:
             first_name, last_name: Имя пользователя, Фамилия пользоввателя

        """
        params = {
            'user_ids': user_id,
            'access_token': self.token,
            'v': self.version,
            'lang': self.lang
        }

        response = requests.get(self.api_url_users, params=params)
        data = response.json()

        if 'response' in data:
            user_info = data['response'][0]
            return user_info.get('first_name', ''), user_info.get('last_name', '')
        else:
            error = data.get('error', 'Unknown error')
            print(f"Error fetching user name for user {user_id}: {error}")
            return '', ''

    def fetch_friends(self, user_id)->str:
        """_summary_

        Args:
            user_id (int): ID пользователя

        Returns:
            List: Список друзей пользователя
        """

        params = {
            'user_id': user_id,
            'access_token': self.token,
            'v': self.version,
            'fields': 'first_name,last_name',
            'lang': self.lang
        }

        response = requests.get(self.api_url_friends, params=params)
        data = response.json()

        if 'response' in data:
            friends = data['response']['items']
            filtered_friends = [
                {
                    'id': friend['id'],
                    'first_name': friend.get('first_name', ''),
                    'last_name': friend.get('last_name', '')
                }
                for friend in friends
            ]
            return filtered_friends
        else:
            error = data.get('error', 'Unknown error')
            print(f"Error fetching friends for user {user_id}: {error}")
            return []

    def save_friends(self, user_id, user_first_name, user_last_name, friends, output_file):
        """Сохраняеn или обновляет список друзей в JSON-файл

        Args:
            user_id (int): ID пользователя
            user_first_name (str): Имя пользователя
            user_last_name (str): Фамилия пользователя
            friends (List): Список друзей
            output_file (str): Путь до файла
        """
        data = {}

        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print("Ошибка при чтении существующего JSON-файла.")
                    data = {}

        data[str(user_id)] = {
            'first_name': user_first_name,
            'last_name': user_last_name,
            'friends': friends
        }
        
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def process_users(self, input_file, output_file):
        """Загружает список пользователей, ищет их друзей и сохраняет результат

        Args:
            input_file (str): Путь до начальных данных
            output_file (str): Путь до итогового файла
        """
        user_ids = self.load_user_ids(input_file)
        
        if not user_ids:
            return
        
        for user_id in user_ids:
    
            user_first_name, user_last_name = self.fetch_user_name(user_id) 
            if user_first_name and user_last_name:
                time.sleep(2) 
                print(f"Fetching friends for user ID {user_id}...")
                friends = self.fetch_friends(user_id)  
                if friends:
                    self.save_friends(user_id, user_first_name, user_last_name, friends, output_file) 
                    print(f"Saved friends for user {user_id}.")


if __name__ == '__main__':

    fetcher = UserFriendsFetcher(token=VK_TOKEN)
    input_file = 'data/group_ids.json'
    output_file = 'data/friends_output.json'

    fetcher.process_users(input_file, output_file)
    visualize_friends_graph(output_file)