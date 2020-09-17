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

    # Load City
    target_osr = osr.SpatialReference()
    target_osr.ImportFromEPSG(4326)
    Sulmona.setSRS(target_osr)

    Sulmona.loadCrossroadsFromShapefile(crossroads_path)
    Sulmona.loadStreetsFromShapefile(streets_path)
    Sulmona.loadBuildingsFromShapefile(buildings_pos_path)
    Sulmona.addBuildingsGeometryFromShapefile(buildings_path)

    Sulmona.loadWaitingAreasFromShapefile(waiting_areas_pos_path)
    Sulmona.addWaitingAreasGeometryFromShapefile(waiting_areas_path)

    Sulmona.loadCensusAreasFromShapefile(census_areas_path)

    ReconstructionGraph = createReconstructionGraph(Sulmona)

    plotCityGraph(ReconstructionGraph)

    saveCityGraph(ReconstructionGraph, 'reconstructionGraph')