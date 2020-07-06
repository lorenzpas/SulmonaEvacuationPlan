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
    if (object.endpoints):
        G.add_edge(object.endpoints[0], object.endpoints[1], edge_type = type, width = object.width, length = object.length, buildings = object.listOfBuildings)


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

for building in Sulmona.Buildings:
    addNode(SulmonaGraph, 'building', Sulmona.Buildings[building])

for w_area in Sulmona.WaitingAreas:
    addNode(SulmonaGraph, 'waiting_area', Sulmona.WaitingAreas[w_area])

for crossroad in Sulmona.Crossroads:
    addNode(SulmonaGraph, 'crossroads', Sulmona.Crossroads[crossroad])

#for street in Sulmona.Streets:
#    addEdge(SulmonaGraph, 'street', Sulmona.Streets[street])


#nx.draw(SulmonaGraph)
#plt.show()

for node in SulmonaGraph.nodes(data=True):
    print (node)



