import csv
import json
from collections import defaultdict


nodes = set()
edges = []
with open("data/friends_output2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# словарь для хранения количества появлений каждого пользователя
appearance_count = defaultdict(int)
nodes = set()
edges = []

def add_connections(user_id, user_first_name, user_last_name, friends):
    appearance_count[user_id] += 1
    user_node = (user_id, user_first_name, user_last_name)
    nodes.add(user_node)
    
    # Проходимся по друзьям, добавляя их как вершины и связи с начальным пользователем
    for friend in friends:
        friend_id = friend["id"]
        friend_node = (friend_id, friend["first_name"], friend["last_name"])
        
        # Увеличиваем счётчик для каждого друга
        appearance_count[friend_id] += 1
        nodes.add(friend_node)
        
        edges.append((user_id, friend_id))
        
        # Если у друга также есть друзья, рекурсивно добавляем их
        if "friends" in friend:
            add_connections(user_id, user_first_name, user_last_name, friend["friends"])

for user_id, user_data in data.items():
    add_connections(user_id, user_data["first_name"], user_data["last_name"], user_data.get("friends", []))

nodes_with_counts = [(user_id, first_name, last_name, appearance_count[user_id]) for user_id, first_name, last_name in nodes]

with open("nodes.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "First Name", "Last Name", "Appearance Count"])
    writer.writerows(nodes_with_counts)

with open("edges.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["Source", "Target"])
    writer.writerows(edges)

print("Файлы созданы!")