from concurrent.futures import ThreadPoolExecutor
import json
import networkx as nx


def calculate_centralities(group_ids_file, friends_data_file):
    """Загрузка данных из файлов

    Args:
        group_ids_file (str): Путь до файла с пользователями, для которых необходимо вывести центральности
        friends_data_file (_type_): Путь до общего файла с метаинформацией пользователей

    Returns:
        dict: Центральности по посреднечеству, близости и собственному вектору
    """
    with open(group_ids_file, encoding='utf-8') as f:
        group_ids = json.load(f)

    with open(friends_data_file, encoding='utf-8') as f:
        friends_data = json.load(f)

    G = nx.Graph()

    def add_friends_to_graph(user_id, friends_list):
        for friend in friends_list:
            friend_id = friend['id']
            G.add_node(friend_id, first_name=friend['first_name'], last_name=friend['last_name'])
            G.add_edge(user_id, friend_id)  

            if 'friends' in friend:
                add_friends_to_graph(friend_id, friend['friends'])

   
    for user_id, user_info in friends_data.items():
        user_id = int(user_id)
        G.add_node(user_id, first_name=user_info['first_name'], last_name=user_info['last_name'])
        add_friends_to_graph(user_id, user_info['friends'])

    
    def calculate_betweenness(G):
        print("Начат расчет betweenness_centrality...")
        return nx.betweenness_centrality(G)

    def calculate_closeness(G):
        print("Начат расчет closeness_centrality...")
        return nx.closeness_centrality(G)

    def calculate_eigenvector(G):
        print("Начат расчет eigenvector_centrality...")
        return nx.eigenvector_centrality(G, max_iter=10000, tol=1e-06)

    num_nodes = G.number_of_nodes()
    print(f'Количество вершин: {num_nodes}')

    num_edges = G.number_of_edges()
    print(f'Количество рёбер: {num_edges}')

    with ThreadPoolExecutor() as executor:
        future_betweenness = executor.submit(calculate_betweenness, G)
        future_closeness = executor.submit(calculate_closeness, G)
        future_eigenvector = executor.submit(calculate_eigenvector, G)

        betweenness_centrality = future_betweenness.result()
        print("Расчет betweenness_centrality закончен")

        closeness_centrality = future_closeness.result()
        print("Расчет closeness_centrality закончен")

        eigenvector_centrality = future_eigenvector.result()
        print("Расчет eigenvector_centrality закончен")

    centralities = {}
    
    for user_id in group_ids:
        centralities[user_id] = {
            'betweenness': betweenness_centrality.get(user_id, 0),
            'closeness': closeness_centrality.get(user_id, 0),
            'eigenvector': eigenvector_centrality.get(user_id, 0)

        }

    return centralities

# centralities = calculate_centralities('data/group_ids.json', 'data/friends_output2.json')


    # 268235974,
    # 200955746,