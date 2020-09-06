from City import *
import networkx as nx
import matplotlib.pyplot as plt

def addNode(G, type, object):
    if (type == 'building'):
        G.add_node(str(object.position), pos = object.position, nodeType=type, buildingType=str(object.buildingType), risk=object.risk, nPeople=object.nPeople)
    if (type == 'crossroad'):
        G.add_node(str(object.position), pos = object.position, nodeType=type)
    if (type =='waiting_area'):
        G.add_node(str(object.position), pos = object.position, nodeType = type, capacity = object.users_capacity)

def addEdge(G, type, object):
    if (object.endpoints and G.has_node(str(object.endpoints[0])) and G.has_node(str(object.endpoints[1]))):
        if (type == 'street'):
            G.add_edge(str(object.endpoints[0]), str(object.endpoints[1]), edgeType = type, width = object.width, length = object.length, risk=object.risk, buildings = buildingsToString(object.listOfBuildings))
        if (type == 'halfstreet'):
            points = object.divideStreetWithBuildings()
            if (points):
                for i in range (0, len(points)-1):
                    G.add_edge(str(points[i]), str(points[i+1]), edgeType = type, width = object.width, risk=object.risk)

def buildingsToString(listOfBuildings):
    buildings = []
    for building in listOfBuildings:
        buildings.append(str(building.ID))
    return buildings

def plotCityGraph(Graph):
    # Plotting graph
    crossroads = []
    buildings = []
    waiting_areas = []
    for node, data in Graph.nodes(data=True):
        if (data):
            if (data['nodeType'] == 'crossroad'):
                crossroads.append(node)
            if (data['nodeType'] == 'building'):
                buildings.append(node)
            if (data['nodeType'] == 'waiting_area'):
                waiting_areas.append(node)
        else:
            print('no nodeType in this node')

    pos = nx.get_node_attributes(Graph, 'pos')

    nx.draw_networkx_nodes(Graph, pos, nodelist=crossroads, node_size=5, node_color='#ff6666', node_shape='o')
    nx.draw_networkx_nodes(Graph, pos, nodelist=buildings, node_size=5, node_color='#1f78b4', node_shape='o')
    nx.draw_networkx_nodes(Graph, pos, nodelist=waiting_areas, node_size=5, node_color='#ffff99', node_shape='o')

    nx.draw_networkx_edges(Graph, pos, edgelist=Graph.edges())
    plt.show()

def loadCompleteGraph():
    Graph = nx.Graph()

    for crossroad in Sulmona.Crossroads:
        addNode(Graph, 'crossroad', Sulmona.Crossroads[crossroad])
    for building in Sulmona.Buildings:
        addNode(Graph, 'building', Sulmona.Buildings[building])
    for w_area in Sulmona.WaitingAreas:
        addNode(Graph, 'waiting_area', Sulmona.WaitingAreas[w_area])
    for street in Sulmona.Streets:
        addEdge(Graph, 'street', Sulmona.Streets[street])
        addEdge(Graph, 'halfstreet', Sulmona.Streets[street])
    return Graph

def loadCrossroadsGraph():
    Graph = nx.Graph()

    for crossroad in Sulmona.Crossroads:
        addNode(Graph, 'crossroad', Sulmona.Crossroads[crossroad])
    for street in Sulmona.Streets:
        addEdge(Graph, 'street', Sulmona.Streets[street])

    return Graph

def saveCityGraph(Graph, name):
    nx.write_adjlist(Graph, str(name)+'.adjlist')
    nx.write_gpickle(Graph, str(name)+'.gpickle')

def loadCityGraph(name):
    #G=nx.read_adjlist(str(name) + '.adjlist')
    G=nx.read_gpickle(str(name) + '.gpickle')
    return G

if __name__ == "__main__":
    Sulmona = City('Sulmona')
    os.chdir('data') #working directory

    buildings_pos_path='buildings/CR01G_EDIFICI_POS.shp' #position of the buildings' shapefile
    buildings_path='buildings/CR01G_EDIFICI.shp' #polygons that represent the buildings
    buildings_MSKClass_path='buildings/Classi_MSK.shp'

    waiting_areas_path = 'waiting_areas/Aree di attesa.shp'
    waiting_areas_pos_path = 'waiting_areas/Aree_di_attesa_pos.shp'

    crossroads_path = 'streets/CR325G_GZ_STR_POS.shp'
    streets_path = 'streets/CR317G_EL_STR_TRAC.shp'

    census_areas_path = 'census_areas/sez_cens_2011_SULMO_con_dati.shp'

    Sulmona.loadCrossroadsFromShapefile(crossroads_path)
    Sulmona.loadStreetsFromShapefile(streets_path)
    Sulmona.loadBuildingsFromShapefile(buildings_pos_path)
    Sulmona.addBuildingsGeometryFromShapefile(buildings_path)

    Sulmona.loadWaitingAreasFromShapefile(waiting_areas_pos_path)
    Sulmona.addWaitingAreasGeometryFromShapefile(waiting_areas_path)

    Sulmona.loadCensusAreasFromShapefile(census_areas_path)

    CompleteGraph=loadCompleteGraph()
    CrossroadsGraph=loadCrossroadsGraph()

    plotCityGraph(CompleteGraph)
    plotCityGraph(CrossroadsGraph)

    saveCityGraph(CompleteGraph, 'completeGraph')
    saveCityGraph(CrossroadsGraph, 'crossroadsGraph')

    #print (CompleteGraph.number_of_edges())
    #print (CrossroadsGraph.number_of_edges())
    #G = loadCityGraph('crossroadsGraph')

    G = nx.read_gpickle('completeGraph.gpickle')
    for node, data in G.nodes(data=True):
        if data['nodeType']== 'building':
            print(node, data)
    #for node in CompleteGraph.nodes(data=True):
    #    print(node)
    #for edge in CompleteGraph.edges(data=True):
     #   print(edge)

    print(CompleteGraph.number_of_nodes())
    print(CompleteGraph.number_of_edges())



