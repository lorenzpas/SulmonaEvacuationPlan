from osgeo import ogr
import os
from shapely.ops import nearest_points
from shapely.wkt import loads
import sys

#load the shapefile of the buildings and streets
drvName = "ESRI Shapefile"
driver = ogr.GetDriverByName(drvName) #a shapefile driver

os.chdir('data') #working directory

#file_buildings = 'buildings/CR01G_EDIFICI.shp' #filename buildings
file_wAreas = 'waiting_areas/Aree di attesa.shp' #filename waitingareas
file_streets = 'streets/CR317G_EL_STR_TRAC.shp' #filename streets
#file_MSK = 'buildings/Classi_MSK.shp' #filename MSK

#vector_buildings = driver.Open(file_buildings, 1) #0-read, 1-writable
#layer_buildings= vector_buildings.GetLayer(0)

vector_wAreas = driver.Open(file_wAreas, 0) #0-read, 1-writable
layer_wAreas= vector_wAreas.GetLayer(0)

vector_streets = driver.Open(file_streets, 0) #0-read, 1-writable
layer_streets= vector_streets.GetLayer(0)

#vector_MSK = driver.Open(file_MSK, 0) #0-read, 1-writable
#layer_MSK= vector_MSK.GetLayer(0)

#Create the layer in which the buildings are positioned on their nearest street


#Open the folder data source for writing
ds = ogr.Open('waiting_areas', 1)
if ds is None:
    sys.exit('Could not open folder.')


#if the layer already exists, delete it
if ds.GetLayer('Aree_di_attesa_POS'):
    ds.DeleteLayer('Aree_di_attesa_POS')

layer_wAreas_pos = ds.CreateLayer('Aree_di_attesa_POS',layer_wAreas.GetSpatialRef(),geom_type=ogr.wkbPoint)
layer_wAreas_pos.CreateFields(layer_wAreas.schema)
idField = ogr.FieldDefn("CR01_STR", ogr.OFTInteger)
layer_wAreas_pos.CreateField(idField)


#Create a blank feature -- it will be used to build a feature in the cycle
out_defn = layer_wAreas_pos.GetLayerDefn()  #it takes the layer definitions
wArea_pos = ogr.Feature(out_defn)   #it uses the layer definitions to allocate a new blank feature

for wArea in layer_wAreas:
    for i in range(wArea.GetFieldCount()): #for all the attributes
        value = wArea.GetField(i)          #takes the value
        wArea_pos.SetField(i, value)          #saves the value in the output feature
    # Insert the temporary feature in the output layer
    layer_wAreas_pos.CreateFeature(wArea_pos)

    #Add geometry finding the building nearest street
    geom_wArea = wArea.GetGeometryRef()  # get feature geometry
    min_dist = 100000000000
    for street in layer_streets:
        geom_street = street.GetGeometryRef()
        distance = geom_wArea.Distance(geom_street)
        if distance < min_dist:
            min_dist = distance
            nearest_street = street
    street_id = nearest_street.GetField('CR317_IDOB')
    #print(street_id)
    wArea_pos.SetField('CR01_STR', street_id)

    # find the nearest point between the building and the finded street
    wkt_street = nearest_street.GetGeometryRef().ExportToWkt()
    wkt_wArea = wArea.GetGeometryRef().ExportToWkt()
    shapely_street = loads(wkt_street)
    shapely_wArea = loads(wkt_wArea)
    np = nearest_points(shapely_street, shapely_wArea)[0]
    wArea_point = ogr.CreateGeometryFromWkt(np.wkt)

    wArea_pos.SetGeometry(wArea_point)
    layer_wAreas_pos.SetFeature(wArea_pos)
    outFeature = None


del ds
vector_wAreas.Destroy()
vector_streets.Destroy()








