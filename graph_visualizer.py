import json
from collections import defaultdict, deque
from pyvis.network import Network
import networkx as nx
from collections import deque


def create_graph_recursive(G, user_id, user_info, visited=None):
    """Рекурсивная функция для добавления пользователей и их друзей в граф, избегая дублирования рёбер."""

    if visited is None:
        visited = set()

    user_name = f"{user_info.get('first_name', 'Unknown')} {user_info.get('last_name', 'Unknown')}"
    G.add_node(user_id, label=user_name)

    visited.add(user_id)

    if 'friends' in user_info:
        for friend in user_info['friends']:
            friend_id = friend.get('id')

            if friend_id not in visited:
                friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"

                G.add_node(friend_id, label=friend_name)

                # Проверка, существует ли уже ребро
                if not G.has_edge(user_id, friend_id):
                    G.add_edge(user_id, friend_id)
                    print(f"Добавлено ребро: {user_id} - {friend_id}")  # Печать добавляемого ребра
                
                if 'friends' in friend:
                    create_graph_recursive(G, friend_id, friend, visited)

def check_friends_structure(friends_data):
    for user_id, user_info in friends_data.items():
        if 'friends' not in user_info or not isinstance(user_info['friends'], list):
            print(f"Пользователь {user_id} не имеет корректной структуры друзей.")
        for friend in user_info['friends']:
            if 'id' not in friend:
                print(f"Друг пользователя {user_id} не имеет ID.")


def create_graph2(friends_data):
    """Функция для создания графа на основе данных из файла, включая друзей всех уровней

    Args:
        friends_data (dict): Данные друзей из JSON файла

    Returns:
        Graph: Граф, включающий всех друзей всех уровней
    """
    G = nx.Graph()

    for user_id, user_info in friends_data.items():
        user_id = int(user_id)
        print(user_id)
        create_graph_recursive(G, user_id, user_info)

    return G

def remove_single_edge_nodes(G):
    """Функция для удаления узлов с одной связью.""

    Args:
        G (graph.Graph): Граф

    Returns:
        graph.Graph: Преобразованный граф
    """
    nodes_to_remove = [node for node, degree in dict(G.degree()).items() if degree == 1]
    G.remove_nodes_from(nodes_to_remove)
    return G

def track_graph_growth(G):
    print(f"Текущий граф: {G.number_of_nodes()} узлов, {G.number_of_edges()} рёбер")

    
def visualize_friends_graph(output_file='data/friends_output2.json', output_html='data/friends_graph.html'):
    """Основная функция для создания/визуализации графа."""
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            friends_data = json.load(f)
    except FileNotFoundError:
        print(f"Файл {output_file} не найден.")
        return
    except json.JSONDecodeError:
        print(f"Ошибка при чтении файла {output_file}")
        return

    check_friends_structure(friends_data)  # Проверка структуры данных

    G = create_graph2(friends_data)

    track_graph_growth(G)  # Вывод размера графа

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f'Количество вершин: {num_nodes}, Количество рёбер: {num_edges}')

    G = remove_single_edge_nodes(G)  # Фильтрация вершин с одним ребром

    net = Network(notebook=True)
    net.from_nx(G)

    net.show(output_html)
    


visualize_friends_graph("data/friends_output2.json")