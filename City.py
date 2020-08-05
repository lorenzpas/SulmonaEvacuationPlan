from osgeo import ogr, osr
import os
from visuallayer import *
from shapely.ops import split, nearest_points
from shapely.geometry import Point, LineString, MultiPoint


class City:

    def __init__(self, CityName):
        self.CityName = CityName
        self.Buildings = {}  # dictionary where the key is the Building ID and the value are the building objects
        self.Crossroads = {}
        self.WaitingAreas = {}
        self.Streets = {}


    def loadCrossroadsFromShapefile(self, path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        crossroads_vector = driver.Open(path, 0)
        crossroads_layer = crossroads_vector.GetLayer(0)
        crossroads_srs = crossroads_layer.GetSpatialRef()

        # Create buildings and set their position and ID of the associated street using the the positin shapefile of the buildings
        for crossroad in crossroads_layer:
            crossroadID = crossroad.GetField('CR325_IDOB')
            crossroad_obj = Crossroad(crossroadID)  # new building
            crossroad_obj.description = crossroad.GetField('CR325_DESC')

            # Position
            crossroad_geom = crossroad.GetGeometryRef()
            #transform_coordinate_to_WGS84(crossroad_geom, crossroads_srs)
            crossroad_obj.setPosition((crossroad_geom.GetX(), crossroad_geom.GetY()))

            self.Crossroads[crossroadID] = crossroad_obj  # Add the the building in the list of the buidings in the city

    def loadStreetsFromShapefile(self, path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        streets_vector = driver.Open(path, 0)
        streets_layer = streets_vector.GetLayer(0)
        streets_srs = streets_layer.GetSpatialRef()

        for street in streets_layer:
            streetID = street.GetField('CR317_IDOB')
            streetName = street.GetField('CR317_Topo')

            street_geom = street.GetGeometryRef()

            street_obj = Street(streetID, streetName)  # create new street
            #transform_coordinate_to_WGS84(street_geom, streets_srs)
            street_obj.wtkGeometry = street_geom.ExportToWkt()  # geoemtry of the stree
            street_obj.length = street.GetField('SHAPE_Leng')  # length of the street
            width_string = street.GetField('CR317_De_1')  # width of the street
            width_types = {'Larghezza maggiore di 7,0 metri': 7, 'Larghezza compresa tra 3,5 metri e 7,0 metri': 5,
                           'Larghezza minore di 3,5 metri': 3}
            if (width_string in width_types):
                street_obj.width = width_types[width_string]
            else:
                street_obj.width = -1

            # load all the descriptions of the road
            street_obj.descriptions.append(street.GetField('CR317_DESC'))
            street_obj.descriptions.append(street.GetField('CR317_De_2'))
            street_obj.descriptions.append(street.GetField('CR317_De_3'))
            street_obj.descriptions.append(street.GetField('CR317_De_4'))
            street_obj.descriptions.append(street.GetField('CR317_De_5'))
            street_obj.descriptions.append(street.GetField('CR317_De_6'))

            # Endpoints
            if (street_geom.GetGeometryName() == 'LINESTRING'):  # n.b. if they are multilinestring it means that we don't have the full street so we can't consider it
                first = street_geom.GetPoint(0)
                last = street_geom.GetPoint(street_geom.GetPointCount() - 1)
                street_obj.endpoints = ((first[0], first[1]), (last[0],last[1]))

            self.Streets[streetID] = street_obj

    def loadBuildingsFromShapefile(self, path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        buildings_pos_vector = driver.Open(path, 0)
        buildings_pos_layer = buildings_pos_vector.GetLayer(0)
        building_pos_srs = buildings_pos_layer.GetSpatialRef()
        # Create buildings and set their position and ID of the associated street using the the positin shapefile of the buildings
        for building in buildings_pos_layer:

            buildingID = building.GetField('CR01_IDOBJ')
            building_obj = Building(buildingID)  # new building

            # Position
            building_geom = building.GetGeometryRef()
            #transform_coordinate_to_WGS84(building_geom, building_pos_srs)
            building_obj.setPosition((building_geom.GetX(), building_geom.GetY()))

            # Associated street ID
            building_obj.setStreetID(building.GetField('CR01_STR'))

            # Associated risk
            risk_string = building.GetField('CR01_MSK')
            risk_type = {'A': 4, 'B': 3, 'C1': 2, 'C2': 1}

            if (risk_string in risk_type):
                building_obj.risk = risk_type[risk_string]
            else:
                building_obj.risk = 0

            streetID = building.GetField('CR01_STR')

            # load all the descriptions of the building
            building_obj.descriptions.append(building.GetField('CR01_DESCR'))
            building_obj.descriptions.append(building.GetField('CR01_DES_1'))
            building_obj.descriptions.append(building.GetField('CR01_DES_2'))
            building_obj.descriptions.append(building.GetField('CR01_DES_3'))
            building_obj.descriptions.append(building.GetField('CR01_DES_4'))
            building_obj.descriptions.append(building.GetField('CR01_DES_5'))

            building_obj.buildingType = building.GetField('CR01_DES_5')

            self.Buildings[buildingID] = building_obj  # Add the the building in the list of the buidings in the city
            self.Streets[streetID].listOfBuildings.append(building_obj)
            if (building_obj.risk > self.Streets[streetID].risk):
                self.Streets[streetID].risk = building_obj.risk

    def addBuildingsGeometryFromShapefile(self, path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        buildings_vector = driver.Open(path, 0)
        buildings_layer = buildings_vector.GetLayer(0)
        building_srs = buildings_layer.GetSpatialRef()

        # Set the geometry and area of the buildings
        for building in buildings_layer:
            # Set geometry and area of the building
            buildingID = building.GetField('CR01_IDOBJ')
            building_geom = building.GetGeometryRef()
            # self.Buildings[buildingID].area = building_geom.Area()
            #transform_coordinate_to_WGS84(building_geom, building_srs)
            self.Buildings[buildingID].wtkGeometry = building_geom.ExportToWkt()

    def loadWaitingAreasFromShapefile(self, path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        w_areas_pos_vector = driver.Open(path, 0)
        w_areas_pos_layer = w_areas_pos_vector.GetLayer(0)
        w_areas_srs = w_areas_pos_layer.GetSpatialRef()

        # Create buildings and set their position and ID of the associated street using the the positin shapefile of the buildings
        for w_area in w_areas_pos_layer:
            wAreaID = w_area.GetField('Id')
            w_area_obj = WaitingArea(wAreaID)  # new waiting area

            w_area_geom = w_area.GetGeometryRef()
            #transform_coordinate_to_WGS84(w_area_geom, w_areas_srs)
            w_area_obj.setPosition((w_area_geom.GetX(), w_area_geom.GetY()))
            # wAreaGeom = w_area.GetGeometryRef()

            # w_area.wtkGeometry = wAreaGeom.ExportToWkt()  # geoemetry of the waiting area
            # note that the surface occupying a person from a standstill is 2.5 square meters/person
            w_area_obj.users_capacity = w_area.GetField('utenti')  # number of users
            w_area_obj.residents_capacity = w_area.GetField('abitanti')  # number of users

            self.WaitingAreas[wAreaID] = w_area_obj

    def addWaitingAreasGeometryFromShapefile(self, path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        w_areas_vector = driver.Open(path, 0)
        w_areas_layer = w_areas_vector.GetLayer(0)
        w_areas_srs = w_areas_layer.GetSpatialRef()

        # Set the geometry and area of the areas
        for wArea in w_areas_layer:
            wAreaID = wArea.GetField('Id')
            w_area_geom = wArea.GetGeometryRef()
            # self.WaitingAreas[wAreaID].area = w_area_geom.Area()
            #transform_coordinate_to_WGS84(w_area_geom, w_areas_srs)
            self.WaitingAreas[wAreaID].wtkGeometry = w_area_geom.ExportToWkt()

    def getBuildingsFromStreetID(self, streetID):
        return City.Streets[streetID].listOfBuildings

    def plotCity(self):
        for building in self.Buildings:
            # print(self.Buildings[building].position)
            # plot(self.Buildings[building].position, 'red')
            print(self.Buildings[building].wtkGeometry)
        for street in self.Streets:
            plot(self.Streets[street].wtkGeometry, 'blue')


class Building:
    def __init__(self, id):
        self.ID = id
        self.addressNumber = None
        self.streetID = None
        self.position = None
        self.wtkGeometry = None
        self.descriptions = []
        self.area = None
        self.risk = None
        self.type = None
        self.nPeople = 3  # ToDO: use censius to find the number of people in every buildings

    def setPosition(self, coordinate):
        self.position = coordinate

    def setStreetID(self, street):
        self.streetID = street


class Crossroad:

    def __init__(self, id):
        self.ID = id
        self.position = None
        self.description = None

    def setPosition(self, coordinate):
        self.position = coordinate


class Street:

    def __init__(self, id, name):
        self.ID = id
        self.name = name
        self.wtkGeometry = None
        self.descriptions = []
        self.width = None
        self.length = None
        self.endpoints = None
        self.listOfBuildings = []
        self.risk = 0

    def divideStreetWithBuildings(self):
        points = []
        buildings = []
        if (self.endpoints):
            points.append((self.endpoints[0][0],self.endpoints[0][1]))
            orig = Point(self.endpoints[0][0],self.endpoints[0][1])
            for building in self.listOfBuildings:
                buildings.append(Point(building.position))
            destinations = MultiPoint(points=list(buildings))

            while (destinations):
                nearest_geoms = nearest_points(orig, destinations)
                nearest_point= nearest_geoms[1]
                points.append((nearest_point.x, nearest_point.y))
                destinations = destinations.difference(nearest_point)
                orig=nearest_point

            points.append((self.endpoints[1][0],self.endpoints[1][1]))
        return points

    def plot(self, color):
        geom = ogr.CreateGeometryFromWkt(self.wtkGeometry)
        plot_geometry(geom, fillcolor=color, alpha=0.2)


class WaitingArea:
    def __init__(self, id):
        self.ID = id
        self.wtkGeometry = None
        self.users_capacity = None
        self.residents_capacity = None

    def setPosition(self, coordinate):
        self.position = coordinate


def transform_coordinate_to_WGS84(object, srs):
    target_osr = osr.SpatialReference()
    target_osr.ImportFromEPSG(4326)
    transformation = osr.CoordinateTransformation(srs, target_osr)
    object.Transform(transformation)
    return object


def plot(wtk, color):
    geom = ogr.CreateGeometryFromWkt(wtk)
    plot_geometry(geom, fillcolor=color, alpha=0.2)


if __name__ == '__main__':
    Sulmona = City('Sulmona')
    os.chdir('data')  # working directory

    buildings_pos_path = 'buildings/CR01G_EDIFICI_POS.shp'  # position of the buildings' shapefile
    buildings_path = 'buildings/CR01G_EDIFICI.shp'  # polygons that represent the buildings
    # buildings_MSKClass_path='buildings/Classi_MSK.shp'

    crossroads_path = 'streets/CR325G_GZ_STR_POS.shp'
    streets_path = 'streets/CR317G_EL_STR_TRAC.shp'

    waiting_areas_path = 'waiting_areas/Aree di attesa.shp'
    waiting_areas_pos_path = 'waiting_areas/Aree_di_attesa_pos.shp'

    Sulmona.loadCrossroadsFromShapefile(crossroads_path)
    Sulmona.loadStreetsFromShapefile(streets_path)
    Sulmona.loadBuildingsFromShapefile(buildings_pos_path)
    Sulmona.addBuildingsGeometryFromShapefile(buildings_path)
    Sulmona.loadWaitingAreasFromShapefile(waiting_areas_pos_path)
    Sulmona.addWaitingAreasGeometryFromShapefile(waiting_areas_path)

    for streetID in Sulmona.Streets:
        street_obj = Sulmona.Streets[streetID]
        street_obj.divideStreetWithBuildings()
        #print(Sulmona.Streets[streetID].descriptions)

    #for building in Sulmona.Buildings:
     #   print (Sulmona.Buildings[building].descriptions)

