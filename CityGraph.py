from City import *
import networkx as nx
import matplotlib.pyplot as plt

def addNode(G, type, object):
    if (type == 'building'):
        G.add_node(object.position, node_type=type, building_type=object.buildingType, risk=object.risk, n_people=object.nPeople)
    if (type == 'crossroad'):
        G.add_node(object.position, node_type=type)
    if (type =='waiting_area'):
        G.add_node(object.position, node_type = type, capacity = object.users_capacity)


def addEdge(G, type, object):
    if (type == 'street'):
        if (object.endpoints):
            if(G.has_node(object.endpoints[0]) and G.has_node(object.endpoints[1])):
                G.add_edge(object.endpoints[0], object.endpoints[1], edge_type = type, width = object.width, length = object.length, risk=object.risk, buildings = object.listOfBuildings)

    if (type == 'halfstreet'):
            points = object.divideStreetWithBuildings()
            for i in range (0, len(points)-1):
                G.add_edge(points[i], points[i+1], edge_type = type, width = object.width, risk=object.risk)

def plotCityGraph(Graph):
    # Plotting graph
    crossroads = []
    buildings = []
    waiting_areas = []
    for node, data in Graph.nodes(data=True):
        if (data['node_type'] == 'crossroad'):
            crossroads.append(node)
        if (data['node_type'] == 'building'):
            buildings.append(node)
        if (data['node_type'] == 'waiting_area'):
            waiting_areas.append(node)

    pos = {}
    for node in Graph.nodes():
        pos[node] = node

    nx.draw_networkx_nodes(Graph, pos, nodelist=crossroads, node_size=5, node_color='#ff6666', node_shape='o')
    nx.draw_networkx_nodes(Graph, pos, nodelist=buildings, node_size=5, node_color='#1f78b4', node_shape='o')
    nx.draw_networkx_nodes(Graph, pos, nodelist=waiting_areas, node_size=5, node_color='#ffff99', node_shape='o')

    nx.draw_networkx_edges(Graph, pos, edgelist=Graph.edges())
    plt.show()

def saveCityGraph(Graph, name):
    nx.write_adjlist(Graph, str(name)+'.adjlist')
   #nx.write_adjlist(Graph, 'data/'+str(name)+'.adjlist')

Sulmona = City('Sulmona')
os.chdir('data') #working directory

buildings_pos_path='buildings/CR01G_EDIFICI_POS.shp' #position of the buildings' shapefile
buildings_path='buildings/CR01G_EDIFICI.shp' #polygons that represent the buildings
buildings_MSKClass_path='buildings/Classi_MSK.shp'

waiting_areas_path = 'waiting_areas/Aree di attesa.shp'
waiting_areas_pos_path = 'waiting_areas/Aree_di_attesa_pos.shp'

crossroads_path = 'streets/CR325G_GZ_STR_POS.shp'
streets_path = 'streets/CR317G_EL_STR_TRAC.shp'


Sulmona.loadCrossroadsFromShapefile(crossroads_path)
Sulmona.loadStreetsFromShapefile(streets_path)
Sulmona.loadBuildingsFromShapefile(buildings_pos_path)
Sulmona.addBuildingsGeometryFromShapefile(buildings_path)

Sulmona.loadWaitingAreasFromShapefile(waiting_areas_pos_path)
Sulmona.addWaitingAreasGeometryFromShapefile(waiting_areas_path)

#Creating Graph of Sulmona
SulmonaGraph = nx.Graph()

for crossroad in Sulmona.Crossroads:
    addNode(SulmonaGraph, 'crossroad', Sulmona.Crossroads[crossroad])
#for building in Sulmona.Buildings:
#    addNode(SulmonaGraph, 'building', Sulmona.Buildings[building])
#for w_area in Sulmona.WaitingAreas:
#    addNode(SulmonaGraph, 'waiting_area', Sulmona.WaitingAreas[w_area])
for street in Sulmona.Streets:
    addEdge(SulmonaGraph, 'street', Sulmona.Streets[street])
    #addEdge(SulmonaGraph, 'halfstreeet', Sulmona.Streets[street])

plotCityGraph(SulmonaGraph)

saveCityGraph(SulmonaGraph, 'crossroadsGraph')

print (SulmonaGraph.degree)
#for edge in SulmonaGraph.edges(data=True):
#    print(edge)


