import json
def checkinfinity(p, source):
    check = False
    checkstring = ""
    for node in p:
        if node == source:
            continue
        checkstring = node
        iterator = node
        while True and p.get(iterator):
            checkstring = checkstring + ':' + p[iterator]
            iterator = p[iterator]
            if iterator == source:
                break
            # print("checkstring = ", end = '')
            # print(checkstring)
            # print("checkstring[:-4]", end = '')
            # print(checkstring[:-4])
            for checking in checkstring[:-4].split(":"):
                if iterator == checking:
                    return True
    return check


def bellman_ford(graph, source):
    # print("Source = ", end="")
    # print(source)
    # Step 1: Prepare the distance and predecessor for each node
    distance, predecessor = dict(), dict()
    for node in graph:
        distance[node], predecessor[node] = float('inf'), None
        if node != source and graph[source].get(node):
            # print('node = ')
            # print(node)
            distance[node], predecessor[node] = graph[source][node], source

    distance[source] = 0
    timerun = 0

    # Step 2: Relax the edges
    for _ in range(len(graph) - 1):
        for node in graph:
            for neighbour in graph[node]:
                # If the distance between the node and the neighbour is lower than the current, store it
                if (neighbour != source) and (distance[neighbour] > distance[node] + graph[node][neighbour]):
                    check_p = predecessor
                    if not checkinfinity(check_p, source):
                        distance[neighbour], predecessor[neighbour] = distance[node] + graph[node][neighbour], node
                    else:
                        return distance, predecessor
                    # # First copy the whole distance
                    # distance_check = distance
                    # check = True
                    # for node in graph:
                    #     for neighbour in graph[node]:
                    #         if distance_check[neighbour] <= distance_check[node] + graph[node][neighbour]:
                    #             check = False
                    # if(check):
                    #
                    # else:
                    #     return distance, predecessor
                    # print('Timerun = ', end='')
                    # print(timerun)
                    # timerun +=1
    #                 print("predecessor = ", end='')
    #                 print(json.dumps(predecessor,indent=4, sort_keys=True))
    #                 print("distance = ", end='')
    #                 print(json.dumps(distance,indent=4, sort_keys=True))
    # print("FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # print("predecessor = ", end='')
    # print(json.dumps(predecessor,indent=4, sort_keys=True))
    # print("distance = ", end='')
    # print(json.dumps(distance,indent=4, sort_keys=True))
    # Step 3: Check for negative weight cycles
    for node in graph:
        for neighbour in graph[node]:
            if (neighbour != source):
              assert distance[neighbour] <= distance[node] + graph[node][neighbour], "Negative weight cycle."

    return distance, predecessor

if __name__ == '__main__':
    graph = {
        'a': {'b': -1, 'c':  4},
        'b': {'c':  3, 'd':  2, 'e':  2},
        'c': {},
        'd': {'b':  1, 'c':  5},
        'e': {'d': -3}
    }

    distance, predecessor = bellman_ford(graph, source='a')

    print(distance)

    graph = {
        'a': {'c': 3},
        'b': {'a': 2},
        'c': {'b': 7, 'd': 1},
        'd': {'a': 6},
    }

    distance, predecessor = bellman_ford(graph, source='a')

    print(distance)
