import os
import requests
import sys

file_path = "adjacency_matrix.txt"
access_token = "pk.eyJ1IjoibGVpZ2hoYWxsaWRheSIsImEiOiJjanVma3E4aGMwZjk0NDVwZzFpcG84M3cwIn0.GrI8s893TPtJfjHzpMMP_A"

def dijkstra(graph, start):
    """    
    Args:
    graph: Adjacency matrix representing the graph. graph[i][j] .
    start: The index of the starting vertex.
    
    Returns:
    dist: A list containing the shortest distance from the starting vertex to each vertex in the graph.
    """
    num_vertices = len(graph)
    dist = [sys.maxsize] * num_vertices
    dist[start] = 0
    visited = [False] * num_vertices
    visit_order = []

    for _ in range(num_vertices):
        u = min_distance(dist, visited)
        visited[u] = True
        visit_order.append(u)
        for v in range(num_vertices):
            if graph[u][v] and not visited[v] and dist[v] > dist[u] + graph[u][v]:
                dist[v] = dist[u] + graph[u][v]

    return (dist, visit_order)

def min_distance(dist, visited):
    """
    
    Args:
    - dist: A list containing the shortest distance from the starting vertex to each vertex in the graph.
    - visited: A list indicating whether a vertex has been visited or not.
    
    Returns:
    - min_index: The index of the vertex with the minimum distance value.
    """
    min_dist = sys.maxsize
    min_index = -1
    for v in range(len(dist)):
        if dist[v] < min_dist and not visited[v]:
            min_dist = dist[v]
            min_index = v
    return min_index

def findIndex (bin_coordinates, bin_id):
    for i, bin in enumerate(bin_coordinates):
        if bin.bin_id == bin_id:
            return i
    return -1

def getDist (start, end):
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{start['lng']},{start['lat']};{end['lng']},{end['lat']}?geometries=geojson&access_token={access_token}"
    response = requests.get(url)
    response_data = response.json()
    return response_data["routes"][0]["distance"]

def update_adjacency_matrix (bin_coordinates, start, start_all_over=0):
    if start_all_over:
        with open(file_path, 'w') as file:
            for i in range(len(bin_coordinates)):
                start_vertex = bin_coordinates[i]
                temp = list()
                temp.append(start_vertex.bin_id)
                for j in range(len(bin_coordinates)):
                    if j<i:
                        end_vertex = bin_coordinates[j]
                        dist = getDist({"lat": start_vertex.latitude, "lng": start_vertex.longitude}, {"lat": end_vertex.latitude, "lng": end_vertex.longitude})
                        temp.append(dist)
                    elif i==j:
                        file.write((' ').join(str(i) for i in temp))
                        if i != len(bin_coordinates)-1:
                            file.write("\n")
                    else:
                        break
    elif os.path.isfile(file_path):
        start_vertex = bin_coordinates[start-1]
        end_vertices = bin_coordinates[:start-1] + bin_coordinates[start:]
        temp = list()
        temp.append(start_vertex.bin_id)
        for end_vertex in end_vertices:
            dist = getDist({"lat": start_vertex.latitude, "lng": start_vertex.longitude}, {"lat": end_vertex.latitude, "lng": end_vertex.longitude})
            temp.append(dist)
        with open(file_path, 'a') as file:
            file.write("\n")
            file.write((' ').join(str(i) for i in temp))
    else:
        with open(file_path, 'w') as file:
            file.write(str(bin_coordinates[start-1].bin_id))

def generate_adjacency_matrix ():
    adjacency_matrix = list()
    bin_ids = list()
    num_nodes = 0
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            data = file.readlines()
            num_nodes = len(data)
            adjacency_matrix.append([0.0]*num_nodes)
            first=True
            for line in data:
                elements_list = line.split()
                if first:
                    bin_ids.append(int(elements_list[0]))
                    first = False
                    continue
                temp = list()
                for element in elements_list:
                    temp.append(float(element))
                bin_id = int(temp.pop(0))
                bin_ids.append(bin_id)
                for i in range(len(temp),num_nodes):
                    temp.append(0.0)
                adjacency_matrix.append(temp)

    for i in range(len(adjacency_matrix)):
        for j in range(i+1,len(adjacency_matrix)):
            adjacency_matrix[i][j] = adjacency_matrix[j][i]
    
    return { "adjacency_matrix": adjacency_matrix, "bin_ids": bin_ids}

def createSubGraph (bins):
    result = generate_adjacency_matrix()
    adjacency_matrix = result["adjacency_matrix"]
    bin_ids = result["bin_ids"]
    totalBins = len(adjacency_matrix)
    indices = list()
    
    for i in range(totalBins):
        if bin_ids[i] in bins:
            indices.append(i)
    
    updatedAdjacencyMatrix = list()
    for i in range(totalBins):
        if i in indices:
            temp = [adjacency_matrix[i][j] for j in indices]
            updatedAdjacencyMatrix.append(temp)
    return updatedAdjacencyMatrix

if __name__ == "__main__":
    # coordinates = [
        # {
            # 'long': 78.05417952272279,
            # 'lat': 27.91144293315685
        # },
        # {
            # 'long': 78.04924271284551,
            # 'lat': 27.896564593387936
        # },
        # {
            # 'long': 78.05696438983387,
            # 'lat': 27.90450742032415
        # },
        # {
            # 'long': 78.0475971095538,
            # 'lat': 27.90450742032415
        # },
        # {
            # 'long': 78.05797706878269,
            # 'lat': 27.890299417245046
        # },
        # {
            # 'long': 78.0459515062621,
            # 'lat': 27.890299417245046
        # },
        # {
            # 'long': 78.05848340825708,
            # 'lat': 27.89768333668161
        # }
    # ]
    
    result = generate_adjacency_matrix()
    adjacency_matrix = result["adjacency_matrix"]
    bin_ids = result["bin_ids"]
    
    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix)):
            print (adjacency_matrix[i][j], end = " ")
        print()
        
    print(f"bin_ids = {bin_ids}")
    
    update_adjacency_matrix = createSubGraph([1,3])
    print(update_adjacency_matrix)