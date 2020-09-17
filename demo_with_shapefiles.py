from CityGraph import *

if __name__ == "__main__":
    Sulmona = City('Centro storico di Sulmona')
    os.chdir('data') #working directory

    buildings_pos_path='buildings/CR01G_EDIFICI_POS.shp' #position of the buildings' shapefile
    buildings_path='buildings/CR01G_EDIFICI.shp' #polygons that represent the buildings
    buildings_MSKClass_path='buildings/Classi_MSK.shp'

    waiting_areas_path = 'waiting_areas/Aree di attesa.shp'
    waiting_areas_pos_path = 'waiting_areas/Aree_di_attesa_pos.shp'

    crossroads_path = 'streets/CR325G_GZ_STR_POS.shp'
    streets_path = 'streets/CR317G_EL_STR_TRAC.shp'

    census_areas_path = 'census_areas/sez_cens_2011_SULMO_con_dati.shp'

    #Load City
    target_osr = osr.SpatialReference()
    target_osr.ImportFromEPSG(4326)
    #Sulmona.setSRS(target_osr)
    Sulmona.loadCrossroadsFromShapefile(crossroads_path)
    Sulmona.loadStreetsFromShapefile(streets_path)
    Sulmona.loadBuildingsFromShapefile(buildings_pos_path)
    Sulmona.addBuildingsGeometryFromShapefile(buildings_path)

    Sulmona.loadWaitingAreasFromShapefile(waiting_areas_pos_path)
    Sulmona.addWaitingAreasGeometryFromShapefile(waiting_areas_path)

    Sulmona.loadCensusAreasFromShapefile(census_areas_path)

    #Create graphs
    CompleteGraph=createCompleteGraph(Sulmona)
    CrossroadsGraph=createCrossroadsGraph(Sulmona)

    #Choose an area of interest
    #p1 = (410673.2, 4656995.6)
    #p2 = (411323.9, 4656994.6)
    #p3 = (411433.2, 4656417.4)
    #p4 = (410757.6, 4656372.7)

    #p1 = (410571.5, 4657179.9)
    #p2 = (411280.2, 4657222.3)
    #p3 = (411413.0, 4656114.5)
    #p4 = (410721.2, 4656148.4)

    p1=(410707.9,4656967.8)
    p2 = (411480.9,4656958.9)
    p3 = (411407.4,4656388.6)
    p4 = (410797.4,4656388.6)
    area = createAreaOfInterest(p1,p2,p3,p4)
    NewGraph = graphFromArea(CompleteGraph, area)

    #Plot the graph in the area of interest
    plotCityGraph(NewGraph)
    plt.savefig('ExampleGraph')
    plt.show()

    #plotCityGraph(CrossroadsGraph)
    #plt.savefig('CrossroadsGraph')


    #saveCityGraph(CompleteGraph, 'completeGraph')
    #saveCityGraph(CrossroadsGraph, 'crossroadsGraph')

    for edge in CompleteGraph.edges(data=True):
       print(edge)



