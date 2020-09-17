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
                    G.add_edge(str(points[i]), str(points[i+1]), edgeType = type, width = object.width, length = getDistance(points[i], points[i+1]), risk=object.risk)

def buildingsToString(listOfBuildings):
    buildings = []
    for building in listOfBuildings:
        buildings.append(str(building.ID))
    return buildings

def getDistance(point1,point2):
    p1 = ogr.Geometry(ogr.wkbPoint)
    p1.AddPoint(point1[0], point1[1])
    p2 = ogr.Geometry(ogr.wkbPoint)
    p2.AddPoint(point2[0], point2[1])
    return  p1.Distance(p2)

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

    #plt.show()

def createCompleteGraph(city):
    Graph = nx.Graph()

    for crossroad in city.Crossroads:
        addNode(Graph, 'crossroad', city.Crossroads[crossroad])
    for building in city.Buildings:
        addNode(Graph, 'building', city.Buildings[building])
    for w_area in city.WaitingAreas:
        addNode(Graph, 'waiting_area', city.WaitingAreas[w_area])
    for street in city.Streets:
        addEdge(Graph, 'street', city.Streets[street])
        addEdge(Graph, 'halfstreet', city.Streets[street])
    return Graph

def createCrossroadsGraph(city):
    Graph = nx.Graph()

    for crossroad in city.Crossroads:
        addNode(Graph, 'crossroad', city.Crossroads[crossroad])
    for street in city.Streets:
        addEdge(Graph, 'street', city.Streets[street])

    return Graph

def createReconstructionGraph(city):
    Graph = nx.Graph()

    for crossroad in city.Crossroads:
        addNode(Graph, 'crossroad', city.Crossroads[crossroad])
    for building in city.Buildings:
        addNode(Graph, 'building', city.Buildings[building])
    for street in city.Streets:
        addEdge(Graph, 'street', city.Streets[street])
        addEdge(Graph, 'halfstreet', city.Streets[street])

    mapping = {}
    nPrivateBuilding = 0
    nBuildingUnderCostruction = 0
    nAgriculturalBuilding = 0
    nChurch = 0
    nFactory = 0

    for node, data in Graph.nodes(data=True):
        if data['nodeType'] == 'building':
            if data['buildingType'] == 'Edificio civile':
                nPrivateBuilding = nPrivateBuilding + 1
                mapping[node] = 'Private building '+str(nPrivateBuilding)
            if data['buildingType'] == 'Edificio in costruzione':
                nBuildingUnderCostruction = nBuildingUnderCostruction + 1
                mapping[node] = 'Building under construction '+str(nBuildingUnderCostruction)
            if data['buildingType'] == 'Edificio agroforestale, stalla, rimessa attrezzi agricoli':
                nAgriculturalBuilding = nAgriculturalBuilding + 1
                mapping[node] = 'Agricultural Building '+str(nAgriculturalBuilding)
            if data['buildingType'] == 'Edificio di culto':
                nChurch = nChurch + 1
                mapping[node] = 'Church '+str(nChurch)
            if data['buildingType'] == 'Stabilimento, opificio':
                nFactory = nFactory + 1
                mapping[node] = 'Factory '+str(nFactory)

        else:
            mapping [node] = node

        RecGraph = nx.relabel_nodes(Graph, mapping)

    return RecGraph

def saveCityGraph(Graph, name):
    nx.write_adjlist(Graph, str(name)+'.adjlist')
    nx.write_gpickle(Graph, str(name)+'.gpickle')

def loadCityGraphFromGpickle(filepath):
    #G=nx.read_adjlist(str(name) + '.adjlist')
    G=nx.read_gpickle(filepath)
    return G

def createAreaOfInterest(p1,p2,p3,p4):
    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(p1[0], p1[1])
    ring.AddPoint(p2[0], p2[1])
    ring.AddPoint(p3[0], p3[1])
    ring.AddPoint(p4[0], p4[1])
    ring.AddPoint(p1[0], p1[1])

    # Create polygon
    area = ogr.Geometry(ogr.wkbPolygon)
    area.AddGeometry(ring)

    return area

def inTheAreaOfInterest(pos, area):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(pos[0],pos[1])
    if point.Within(area):
        return True
    else:
        return False

def graphFromArea(G, area):
    subnodes = []
    for node, data in G.nodes(data=True):
        if inTheAreaOfInterest(data['pos'], area):
            subnodes.append(node)

    return G.subgraph(subnodes)


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

    CompleteGraph = createCompleteGraph(Sulmona)
    CrossroadsGraph = createCrossroadsGraph(Sulmona)
    ReconstructionGraph = createReconstructionGraph(Sulmona)

    plotCityGraph(CompleteGraph)
    plotCityGraph(CrossroadsGraph)
    #plotCityGraph(ReconstructionGraph)

    saveCityGraph(CompleteGraph, 'completeGraph')
    saveCityGraph(CrossroadsGraph, 'crossroadsGraph')
    saveCityGraph(ReconstructionGraph, 'recostructionGraph')

    #print (CompleteGraph.number_of_edges())
    #print (CrossroadsGraph.number_of_edges())
    #G = loadCityGraph('crossroadsGraph')

    #G = nx.read_gpickle('completeGraph.gpickle')
    #for node, data in G.nodes(data=True):
    #    if data['nodeType']== 'building':
    #        print(node, data)

    #for node in ReconstructionGraph.nodes(data=True):
    #    print(node)
    for edge in CompleteGraph.edges(data=True):
        print(edge)

    print(CompleteGraph.number_of_nodes())
    print(CompleteGraph.number_of_edges())



