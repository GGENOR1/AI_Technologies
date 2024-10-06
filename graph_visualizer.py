import json
from collections import defaultdict, deque
from pyvis.network import Network
import networkx as nx
from collections import deque


def create_graph_recursive(G, user_id, user_info):
    """Рекурсивная функция для добавления пользователей и их друзей в граф.

    Args:
        G graph.Graph: Граф
        user_id (int): ID пользователя
        user_info (dict): Метаинформация о пользователе

    """
    
    user_name = f"{user_info.get('first_name', 'Unknown')} {user_info.get('last_name', 'Unknown')}"
    G.add_node(user_id, label=user_name)
    
    if 'friends' in user_info:
        for friend in user_info['friends']:
            friend_id = friend.get('id')
            friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"

            G.add_node(friend_id, label=friend_name)
            G.add_edge(user_id, friend_id)

            if 'friends' in friend:
                create_graph_recursive(G, friend_id, friend)


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

# def remove_single_edge_nodes(G):
#     """Функция для удаления узлов с одной связью.""

#     Args:
#         G (graph.Graph): Граф

#     Returns:
#         graph.Graph: Преобразованный граф
#     """
#     return G.subgraph([node for node, degree in dict(G.degree()).items() if degree > 1])

def visualize_friends_graph(output_file='"data/friends_output2.json"', output_html='data/friends_graph.html'):
    """Основная функция для создания/визуализации графа.

    Args:
        output_file (str, optional): Путь до файла со списком пользователей. По умолчанию'"data/friends_output2.json"'.
        output_html (str, optional): Путь для сохранения файла с графом. По умолчанию 'data/friends_graph.html'.
    """
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            friends_data = json.load(f)
    except FileNotFoundError:
        print(f"Файл {output_file} не найден.")
        return
    except json.JSONDecodeError:
        print(f"Ошибка при чтении файла {output_file}")
        return
    
    G = create_graph2(friends_data)
    G = remove_single_edge_nodes(G)
    
    net = Network(notebook=True)
    net.from_nx(G)
    net.show(output_html)
    


visualize_friends_graph("data/friends_output2.json")