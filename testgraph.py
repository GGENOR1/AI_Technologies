import json
import networkx as nx

# Загружаем JSON-файл
with open('data/friends_output2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Создаем граф
G = nx.Graph()

# Рекурсивная функция для добавления узлов и ребер
def add_edges(person):
    user_id = person['id']
    G.add_node(user_id, first_name=person['first_name'], last_name=person['last_name'])
    
    for friend in person.get('friends', []):
        friend_id = friend['id']
        G.add_node(friend_id, first_name=friend['first_name'], last_name=friend['last_name'])
        G.add_edge(user_id, friend_id)
        add_edges(friend)  # Рекурсивно обрабатываем друзей друзей

# Инициализируем обработку с первого пользователя
for user_id, info in data.items():
    add_edges({"id": int(user_id), "first_name": info["first_name"], "last_name": info["last_name"], "friends": info["friends"]})

# Получаем количество узлов и ребер
nodes_count = G.number_of_nodes()
edges_count = G.number_of_edges()

# Экспортируем данные в Excel
# df = pd.DataFrame({
#     'Metric': ['Nodes', 'Edges'],
#     'Count': [nodes_count, edges_count]
# })
# df.to_excel('graph_metrics.xlsx', index=False)

print("Количество узлов:", nodes_count)
print("Количество ребер:", edges_count)