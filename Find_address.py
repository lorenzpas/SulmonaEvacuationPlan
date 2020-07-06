from osgeo import ogr
import os
from shapely.ops import nearest_points
from shapely.wkt import loads
import sys

#load the shapefile of the buildings and streets
drvName = "ESRI Shapefile"
driver = ogr.GetDriverByName(drvName) #a shapefile driver

os.chdir('data') #working directory

file_buildings = 'buildings/CR01G_EDIFICI.shp' #filename buildings
file_streets = 'streets/CR317G_EL_STR_TRAC.shp' #filename streets
file_MSK = 'buildings/Classi_MSK.shp' #filename MSK

vector_buildings = driver.Open(file_buildings, 1) #0-read, 1-writable
layer_buildings= vector_buildings.GetLayer(0)


vector_streets = driver.Open(file_streets, 0) #0-read, 1-writable
layer_streets= vector_streets.GetLayer(0)

vector_MSK = driver.Open(file_MSK, 0) #0-read, 1-writable
layer_MSK= vector_MSK.GetLayer(0)

#Create the layer in which the buildings are positioned on their nearest street

#Open the folder data source for writing
ds = ogr.Open('buildings', 1)
if ds is None:
    sys.exit('Could not open folder.')

#if the layer already exists, delete it
if ds.GetLayer('CR01G_EDIFICI_POS'):
    ds.DeleteLayer('CR01G_EDIFICI_POS')

layer_buildings_pos = ds.CreateLayer('CR01G_EDIFICI_POS',layer_buildings.GetSpatialRef(),geom_type=ogr.wkbPoint)
layer_buildings_pos.CreateFields(layer_buildings.schema)
idField = ogr.FieldDefn("CR01_STR", ogr.OFTInteger)
MSKField = ogr.FieldDefn("CR01_MSK", ogr.OFTString)
layer_buildings_pos.CreateField(idField)
layer_buildings_pos.CreateField(MSKField)

#Create a blank feature -- it will be used to build a feature in the cycle
out_defn = layer_buildings_pos.GetLayerDefn()  #it takes the layer definitions
building_pos = ogr.Feature(out_defn)   #it uses the layer definitions to allocate a new blank feature

building=layer_buildings.GetNextFeature()
while building is not None:
    for i in range(building.GetFieldCount()): #for all the attributes
        value = building.GetField(i)          #takes the value
        building_pos.SetField(i, value)          #saves the value in the output feature
    # Insert the temporary feature in the output layer
    layer_buildings_pos.CreateFeature(building_pos)

    #Add geometry finding the building nearest street
    geom_building = building.GetGeometryRef()  # get feature geometry
    min_dist = 100000000000
    for street in layer_streets:
        geom_street = street.GetGeometryRef()
        distance = geom_building.Distance(geom_street)
        if distance < min_dist:
            min_dist = distance
            nearest_street = street
    street_id = nearest_street.GetField('CR317_IDOB')
    #print(street_id)
    building_pos.SetField('CR01_STR', street_id)

    for buildingMSK in layer_MSK:
        geom_building_MSK = buildingMSK.GetGeometryRef()
        if (geom_building.Intersects(geom_building_MSK)):
            print(buildingMSK.items())
            msk = buildingMSK.GetField('classe_MSK')
            building_pos.SetField('CR01_MSK', msk)

    # find the nearest point between the building and the finded street
    wkt_street = nearest_street.GetGeometryRef().ExportToWkt()
    wkt_building = building.GetGeometryRef().ExportToWkt()
    shapely_street = loads(wkt_street)
    shapely_building = loads(wkt_building)
    np = nearest_points(shapely_street, shapely_building)[0]
    building_point = ogr.CreateGeometryFromWkt(np.wkt)

    building_pos.SetGeometry(building_point)
    layer_buildings_pos.SetFeature(building_pos)
    outFeature = None

    building=layer_buildings.GetNextFeature()

del ds
vector_buildings.Destroy()
vector_streets.Destroy()








