import json
from collections import defaultdict, deque
from pyvis.network import Network
import networkx as nx
from collections import deque


def create_graph(friends_data):
    """Функция для создания графа на основе данных из файла

    Args:
        friends_data (str): Путь до файла

    Returns:
        Graph: Graph
    """
    G = nx.Graph()
    for user_id, user_info in friends_data.items():
        user_id = int(user_id)
        for friend in user_info['friends']:
            friend_id = friend['id']
            G.add_edge(user_id, friend_id)
    return G


def calculate_centralities(subgraph):
    """Расчет характеристик центральностей

    Args:
        subgraph: Граф

    Returns:
        str: betweenness, closeness, eigenvector
    """
    betweenness = nx.betweenness_centrality(subgraph)
    closeness = nx.closeness_centrality(subgraph)
    eigenvector = nx.eigenvector_centrality(subgraph)
    return {
        'betweenness': betweenness,
        'closeness': closeness,
        'eigenvector': eigenvector
    }


def create_graph_for_component(component, friends_data, centralities, net, base_color):
    """Задаем характеристики подграфов
    
    Args:
        component (set): подграф
        friends_data (dict): Список друзей
        centralities (dict): Центральности
        net (pyvis.network.Network): Граф
        base_color (str): Базовый цвет
    """
 
    def normalize(value, min_value, max_value):
        return (value - min_value) / (max_value - min_value) if max_value > min_value else 0.5

    betweenness_values = [centralities['betweenness'].get(user_id, 0) for user_id in component]
    closeness_values = [centralities['closeness'].get(user_id, 0) for user_id in component]
    eigenvector_values = [centralities['eigenvector'].get(user_id, 0) for user_id in component]
    
    min_betweenness, max_betweenness = min(betweenness_values), max(betweenness_values)
    min_closeness, max_closeness = min(closeness_values), max(closeness_values)
    min_eigenvector, max_eigenvector = min(eigenvector_values), max(eigenvector_values)

    for user_id in component:
        user_info = friends_data.get(str(user_id), {})
        if not user_info:
            continue

        user_first_name = user_info.get('first_name', 'Unknown')  
        user_last_name = user_info.get('last_name', 'Unknown')   
        
        betweenness = centralities['betweenness'].get(user_id, 0)
        closeness = centralities['closeness'].get(user_id, 0)
        eigenvector = centralities['eigenvector'].get(user_id, 0)

        node_size = 10 + normalize(betweenness, min_betweenness, max_betweenness) * 40  
        node_color = f"rgb({int(255 * normalize(closeness, min_closeness, max_closeness))}, 0, {int(255 * (1 - normalize(closeness, min_closeness, max_closeness)))} )"

        user_name = f"{user_first_name} {user_last_name}\nCloseness: {closeness:.2f}\nBetweenness: {betweenness:.2f}\nEigenvector: {eigenvector:.2f}"
        
        net.add_node(user_id, label=user_name, color=node_color, size=node_size) 

        for friend in user_info.get('friends', []):
            friend_id = friend['id']
            friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"

            friend_betweenness = centralities['betweenness'].get(friend_id, 0)
            friend_closeness = centralities['closeness'].get(friend_id, 0)
            friend_eigenvector = centralities['eigenvector'].get(friend_id, 0)

            friend_size = 10 + normalize(friend_betweenness, min_betweenness, max_betweenness) * 40
            friend_color = f"rgb({int(255 * normalize(friend_closeness, min_closeness, max_closeness))}, 0, {int(255 * (1 - normalize(friend_closeness, min_closeness, max_closeness)))} )"

            friend_title = (f"Closeness: {friend_closeness:.4f}\n"
                            f"Betweenness: {friend_betweenness:.4f}\n"
                            f"Eigenvector: {friend_eigenvector:.4f}")
            
            net.add_node(friend_id, label=friend_name, title=friend_title, color=friend_color, size=friend_size)  
            net.add_edge(user_id, friend_id)


def save_graph_to_file(graph, output_html='data/friends_graph.html'):
    """Сохраняет файл

    Args:
        graph (pyvis.network.Network): Визуализация
        output_html (str, optional): Путь, куда необходимо сохранить файл. По умолчанию 'data/friends_graph.html'.
    """
    graph.show(output_html)


def visualize_friends_graph(output_file='data/friends_output.json', output_html='data/friends_graph.html'):
    """Основаная функция для создания/визуализации графа

    Args:
        output_file (str, optional): Путь до файла с данными о пользователях. По умолчанию 'data/friends_output.json'.
        output_html (str, optional): Путь, куда необходимо сохранить файл. По умолчанию 'data/friends_graph.html'.
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

    G = create_graph(friends_data)
    
    connected_components = list(nx.connected_components(G))

    net = Network(notebook=True)

    for i, component in enumerate(connected_components):
        subgraph = G.subgraph(component)
        centralities = calculate_centralities(subgraph)
        color = f"#{i:02x}{255 - i:02x}{i * 5 % 255:02x}"
        create_graph_for_component(component, friends_data, centralities, net, color)

    save_graph_to_file(net, output_html)
