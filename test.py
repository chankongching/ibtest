import exec

graph_bidprice, graph_bidprice_inverse, graph_volume = exec.generateGraph()
# Use inverse to calculate nodes graph_bidprice_inverse
nested_d, nested_p = exec.generatebellmanford(graph_bidprice)
print('graph_volume = ')
print(graph_volume)
