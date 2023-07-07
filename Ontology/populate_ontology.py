from owlready2 import *
import pandas as pd

# Load the ontology with imported ontologies
onto_path.append("C:/Users/giorg/OneDrive/Desktop/ontology_2/")
onto = get_ontology("http://example.org/SORSontology").load()

sosa = onto.imported_ontologies[0]
wh_ont = onto.imported_ontologies[1]

time = onto.imported_ontologies[1].imported_ontologies[0]

land_sensor = sosa.Sensor.instances()[3]
sent_sensor = sosa.Sensor.instances()[1]
nasa1_sensor = sosa.Sensor.instances()[0]
nasa2_sensor = sosa.Sensor.instances()[2]
print(land_sensor, sent_sensor, nasa1_sensor, nasa2_sensor)
alg = onto.FPN_Segmentation


# Open csv to read postprocessed data
df = pd.read_csv('C:/Users/giorg/OneDrive/Desktop/ontology/glaciers_analysis.csv')

c = 0
# Loop all over the DataFrame: each row corresponds to a new entity in the ontology
for index, row in df.iterrows():
    if c ==0:
        # Create a SatelliteImage instance and gives it 
        # hasName, hasTile, isProcessedBy, hasPath, hasRow,
        # hasLocation, hasLat and hasLong property
        observation = onto.LandsatImage(row['image_name'][:-4])
        print(observation.iri)
        
        observation.hasName = row['image_name']
        print(observation.get_properties())
        
        observation.hasTile = row['Tile']
        print(list(onto.hasTile.get_relations()))

        observation.isProcessedBy = ["FPN_Segmentation"]
        print(observation.isProcessedBy)

        observation.hasPath = row['WRS_Path']
        observation.hasRow = row['WRS_Row']
        print(observation.hasPath, observation.hasRow)

        observation.hasLocation = row['Country']
        print(observation.hasLocation)

        observation.hasLat = row['Latitude']
        observation.hasLong = row['Longitude']
        print(observation.hasLat, observation.hasLong)
        
        
        # Create Instant instance related to observation, give it inXSDDate property and links observation to it
        date = time.Instant(row['image_name'][:-4]+'_'+row['Date'])
        print(date)
        #slice_9_img_083_2007-11-27
        date.hasDate = row['Date']
        print(date.hasDate)

        observation.hasObservationTime = [date]
        print(observation.hasObservationTime)

        # Create FeatureOfInterest instance and links it to the related observation
        foi = sosa.FeatureOfInterest('HKH_glaciers_in_'+row['image_name'][:-4]+'_'+row['Date'])
        print(foi)
        
        foi.isFeatureOfInterestOf = [observation]
        print(foi.isFeatureOfInterestOf)
        
        # Create CleanIcePercentage, DebrisPercentage and TerrainPercentage and links them to the related observation and algorithm
        ice_perc = onto.CleanIcePercentage('ice_percentage_in_'+row['image_name'][:-4]+'_'+row['Date'])
        print(ice_perc)
        debris_perc = onto.DebrisPercentage('debris_percentage_in_'+row['image_name'][:-4]+'_'+row['Date'])
        print(debris_perc)
        back_perc = onto.TerrainPercentage('background_percentage_in_'+row['image_name'][:-4]+'_'+row['Date'])
        print(back_perc)
        
        ice_perc.isResultOf = [observation]
        debris_perc.isResultOf = [observation]
        back_perc.isResultOf = [observation]
        print(list(sosa.isResultOf.get_relations()))

        ice_perc.isObtainedThrough = ["FPN_Segmentation"]
        debris_perc.isObtainedThrough = ["FPN_Segmentation"]
        back_perc.isObtainedThrough = ["FPN_Segmentation"]

        ice_perc.hasValue = row['CleanIcePercentage']
        debris_perc.hasValue = row['DebrisIcePercentage']
        back_perc.hasValue = row['BackgroundPercentage']
        print(list(onto.isObtainedThrough.get_relations()))


        # Create WeatherState instance
        w_state = wh_ont.WeatherState('WeatherState_in_'+row['image_name'][:-4]+'_'+row['Date'])
        w_state.hasObservationTime = [date]
        w_state.hasLat = row['Latitude']
        w_state.hasLong = row['Longitude']
        w_state.refersTo = [observation]
        print(w_state.hasObservationTime)
        
        # Create Temperature instances with related properties
        avg_temp = onto.AvgTemperature(row['image_name'][:-4]+'_'+row['Date']+'_avg_temperature')
        avg_temp.hasValue = row['AvgTemp']
        avg_temp.isPropertyOf = foi
        max_temp = onto.MaxTemperature(row['image_name'][:-4]+'_'+row['Date']+'_max_temperature')
        max_temp.hasValue = row['MaxTemp']
        max_temp.isPropertyOf = foi
        min_temp = onto.MinTemperature(row['image_name'][:-4]+'_'+row['Date']+'_min_temperature')
        min_temp.hasValue = row['MinTemp']
        min_temp.isPropertyOf = foi
        print(avg_temp.hasValue, min_temp.hasValue, max_temp.hasValue)
        
        observation.observedProperty = [avg_temp, max_temp, min_temp]
        print(observation.observedProperty)

        w_state.hasWeatherPhenomenon = [avg_temp, max_temp, min_temp]
        print(w_state.hasWeatherPhenomenon)


        # Create Spatial Properties (Elevation and Slope)
        ### Elevation
        ice_elev = onto.mean_elevation(row['image_name'][:-4]+'_'+row['Date']+'_mean_ice_elevation')
        debris_elev = onto.mean_elevation(row['image_name'][:-4]+'_'+row['Date']+'_mean_debris_elevation')
        back_elev = onto.mean_elevation(row['image_name'][:-4]+'_'+row['Date']+'_mean_back_elevation')
        
        ice_elev.hasValue = row['MeanIceElevation']
        debris_elev.hasValue = row['MeanDebrisElevation']
        back_elev.hasValue = row['MeanBackgroundElevation']
        ice_elev.isPropertyOf = foi
        debris_elev.isPropertyOf = foi
        back_elev.isPropertyOf = foi
        ice_elev.isObservedBy = [nasa1_sensor, nasa2_sensor]
        debris_elev.isObservedBy = [nasa1_sensor, nasa2_sensor]
        back_elev.isObservedBy = [nasa1_sensor, nasa2_sensor]
        observation.observedProperty.append(ice_elev)
        observation.observedProperty.append(debris_elev)
        observation.observedProperty.append(back_elev)
        print(ice_elev.hasValue, debris_elev.hasValue, back_elev.hasValue)
        
        ### Slope
        ice_slope = onto.mean_slope(row['image_name'][:-4]+'_'+row['Date']+'_mean_ice_slope')
        debris_slope = onto.mean_slope(row['image_name'][:-4]+'_'+row['Date']+'_mean_debris_slope')
        back_slope = onto.mean_slope(row['image_name'][:-4]+'_'+row['Date']+'_mean_back_slope')
        
        ice_slope.hasValue = row['MeanIceSlope']
        debris_slope.hasValue = row['MeanDebrisSlope']
        back_slope.hasValue = row['MeanBackgroundSlope']
        ice_slope.isPropertyOf = foi
        debris_slope.isPropertyOf = foi
        back_slope.isPropertyOf = foi
        ice_slope.isObservedBy = [nasa1_sensor, nasa2_sensor]
        debris_slope.isObservedBy = [nasa1_sensor, nasa2_sensor]
        back_slope.isObservedBy = [nasa1_sensor, nasa2_sensor]
        observation.observedProperty.append(ice_slope)
        observation.observedProperty.append(debris_slope)
        observation.observedProperty.append(back_slope)
        print(ice_slope.hasValue, debris_slope.hasValue, back_slope.hasValue)
        print(list(onto.isPropertyOf.get_relations()))
        

        # Create Spectral Properties (NDVI, NDWI and NDSI)
        ### NDVI
        ice_NDVI = onto.mean_NDVI(row['image_name'][:-4]+'_'+row['Date']+'_mean_ice_NDVI')
        debris_NDVI = onto.mean_NDVI(row['image_name'][:-4]+'_'+row['Date']+'_mean_debris_NDVI')
        back_NDVI = onto.mean_NDVI(row['image_name'][:-4]+'_'+row['Date']+'_mean_back_NDVI')
        
        ice_NDVI.hasValue = row['MeanIceNDVI']
        debris_NDVI.hasValue = row['MeanDebrisNDVI']
        back_NDVI.hasValue = row['MeanBackgroundNDVI']
        ice_NDVI.isPropertyOf = foi
        debris_NDVI.isPropertyOf = foi
        back_NDVI.isPropertyOf = foi
        ice_NDVI.isObservedBy = [land_sensor]
        debris_NDVI.isObservedBy = [land_sensor]
        back_NDVI.isObservedBy = [land_sensor]
        observation.observedProperty.append(ice_NDVI)
        observation.observedProperty.append(debris_NDVI)
        observation.observedProperty.append(back_NDVI)
        print(ice_NDVI.hasValue, debris_NDVI.hasValue, back_NDVI.hasValue)
        
        ### NDSI
        ice_NDSI = onto.mean_NDSI(row['image_name'][:-4]+'_'+row['Date']+'_mean_ice_NDSI')
        debris_NDSI = onto.mean_NDSI(row['image_name'][:-4]+'_'+row['Date']+'_mean_debris_NDSI')
        back_NDSI = onto.mean_NDSI(row['image_name'][:-4]+'_'+row['Date']+'_mean_back_NDSI')
        
        ice_NDSI.hasValue = row['MeanIceNDSI']
        debris_NDSI.hasValue = row['MeanDebrisNDSI']
        back_NDSI.hasValue = row['MeanBackgroundNDSI']
        ice_NDSI.isPropertyOf = foi
        debris_NDSI.isPropertyOf = foi
        back_NDSI.isPropertyOf = foi
        ice_NDSI.isObservedBy = [land_sensor]
        debris_NDSI.isObservedBy = [land_sensor]
        back_NDSI.isObservedBy = [land_sensor]
        observation.observedProperty.append(ice_NDSI)
        observation.observedProperty.append(debris_NDSI)
        observation.observedProperty.append(back_NDSI)
        print(ice_NDSI.hasValue, debris_NDSI.hasValue, back_NDSI.hasValue)
        
        ### NDWI
        ice_NDWI = onto.mean_NDWI(row['image_name'][:-4]+'_'+row['Date']+'_mean_ice_NDWI')
        debris_NDWI = onto.mean_NDWI(row['image_name'][:-4]+'_'+row['Date']+'_mean_debris_NDWI')
        back_NDWI = onto.mean_NDWI(row['image_name'][:-4]+'_'+row['Date']+'_mean_back_NDWI')
        
        ice_NDWI.hasValue = row['MeanIceNDWI']
        debris_NDWI.hasValue = row['MeanDebrisNDWI']
        back_NDWI.hasValue = row['MeanBackgroundNDWI']
        ice_NDWI.isPropertyOf = foi
        debris_NDWI.isPropertyOf = foi
        back_NDWI.isPropertyOf = foi
        ice_NDWI.isObservedBy = [land_sensor]
        debris_NDWI.isObservedBy = [land_sensor]
        back_NDWI.isObservedBy = [land_sensor]
        observation.observedProperty.append(ice_NDWI)
        observation.observedProperty.append(debris_NDWI)
        observation.observedProperty.append(back_NDWI)
        print(ice_NDWI.hasValue, debris_NDWI.hasValue, back_NDWI.hasValue)
        
        ice_perc.hasMean = [ice_elev, ice_slope, ice_NDVI, ice_NDSI, ice_NDWI]
        debris_perc.hasMean = [debris_elev, debris_slope, debris_NDVI, debris_NDSI, debris_NDWI]
        back_perc.hasMean = [back_elev, back_slope, back_NDVI, back_NDSI, back_NDWI]

        
        c +=1
    else:
        pass

'''onto.save(file = "C:/Users/giorg/OneDrive/Desktop/ontology/SORSpopulated.owl", format = "rdfxml")
wh_ont.save(file = "C:/Users/giorg/OneDrive/Desktop/ontology/WeatherOntology1.owl", format = "rdfxml")
sosa.save(file = "C:/Users/giorg/OneDrive/Desktop/ontology/sosa1.owl", format = "rdfxml")
time.save(file = "C:/Users/giorg/OneDrive/Desktop/ontology/time1.owl", format = "rdfxml")'''