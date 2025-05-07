from owlready2 import *
import pandas as pd
import csv

# Load the ontology with imported ontologies
onto_path.append("C:/Users/Giacomo/Desktop/ontology/")
onto = get_ontology("http://example.org/SORSontology").load()

sosa = onto.imported_ontologies[0]
wh_ont = onto.imported_ontologies[1]

time = onto.imported_ontologies[1].imported_ontologies[0]


land_sensor = sosa.Sensor.instances()[3]
sent_sensor = sosa.Sensor.instances()[1]
nasa1_sensor = sosa.Sensor.instances()[0]
nasa2_sensor = sosa.Sensor.instances()[2]

alg = onto.FPN_Segmentation

# Open csv to read postprocessed data
df = pd.read_csv('C:/Users/Giacomo/Desktop/ontology/deforestation.csv')

c = 0
# Loop all over the DataFrame: each row corresponds to a new entity in the ontology
for index, row in df.iterrows():
    if c ==0:
        # Create a SatelliteImage instance and gives it 
        # hasName, hasTile, isProcessedBy, hasPath, hasRow,
        # hasLocation, hasLatitude and hasLogitude property
        observation = onto.LandsatImage(row['image_name'][:-4])

        observation.hasName = row['image_name']

        observation.hasTile = row['Tile']

        observation.isProcessedBy = ["FPN_Segmentation"]

        observation.hasTileNumberField = row['hasTileNumberField']
        observation.hasOrbitNumber = row['hasOrbitNumber']

        observation.hasLocation = row['Location']

        observation.hasLat = row['Latitude']
        observation.hasLong = row['Longitude']
        
        
        # Create Instant instance related to observation, give it inXSDDate property and links observation to it
        date = time.Instant(row['image_name'][:-4]+'_'+row['DateTime'][0:10])

        date.hasDate = row['DateTime']

        observation.hasObservationTime = [date]

        # Create FeatureOfInterest instance and links it to the related observation
        foi = sosa.FeatureOfInterest('Amazon_Forest_in_'+row['image_name'][:-4]+'_'+row['DateTime'][0:10])

        foi.isFeatureOfInterestOf = [observation]

        # Create NoForestPercentage, ForestPercentage and links them to the related observation and algorithm
        noforest_perc = onto.NoForestPercentage('noforest_percentage_in_'+row['image_name'][:-4]+row['DateTime'][0:10])
        forest_perc = onto.ForestPercentage('forest_percentage_in_'+row['image_name'][:-4]+row['DateTime'][0:10])

        noforest_perc.isResultOf = [observation]
        forest_perc.isResultOf = [observation]

        noforest_perc.isObtainedThrough = ['FPN_Segmentation']
        forest_perc.isObtainedThrough = ['FPN_Segmentation']

        noforest_perc.hasValue = row['NoForestPercentage']
        forest_perc.hasValue = row['ForestPercentage']


        # Create WeatherState instance
        w_state = wh_ont.WeatherState('WeatherState_in_'+row['image_name'][:-4]+'_'+row['DateTime'][0:10])
        w_state.hasObservationTime = [date]
        w_state.hasLat = row['Latitude']
        w_state.hasLong = row['Longitude']
        w_state.refersTo = [observation]
        
        # Create Temperature instances with related properties
        avg_temp = onto.AvgTemperature(row['image_name'][:-4]+row['DateTime'][0:10]+'_avg_temperature')
        avg_temp.hasValue = row['AvgTemp']
        avg_temp.isPropertyOf = foi
        max_temp = onto.MaxTemperature(row['image_name'][:-4]+row['DateTime'][0:10]+'_max_temperature')
        max_temp.hasValue = row['MaxTemp']
        max_temp.isPropertyOf = foi
        min_temp = onto.MinTemperature(row['image_name'][:-4]+row['DateTime'][0:10]+'_min_temperature')
        min_temp.hasValue = row['MinTemp']
        min_temp.isPropertyOf = foi

        # Create Temperature instances with related properties
        tot_prec = wh_ont.precipitation(row['image_name'][:-4]+row['DateTime'][0:10]+'_precipitation')
        tot_prec.hasIntensity = [row['TotPrecipitation']]
        tot_prec.isPropertyOf = foi
       
        observation.observedProperty = [avg_temp, max_temp, min_temp, tot_prec]
        print(observation.observedProperty)

        w_state.hasWeatherPhenomenon = [avg_temp, max_temp, min_temp, tot_prec]


        # Create Spectral Properties (NDVI, MSAVI)
        ### NDVI
        noforest_NDVI = onto.mean_NDVI(row['image_name'][:-4]+row['DateTime'][0:10]+'_mean_noforest_NDVI')
        forest_NDVI = onto.mean_NDVI(row['image_name'][:-4]+row['DateTime'][0:10]+'_mean_forest_NDVI')

        noforest_NDVI.hasValue = row['MeanNoForestNDVI']
        forest_NDVI.hasValue = row['MeanForestNDVI']
        noforest_NDVI.isPropertyOf = foi
        forest_NDVI.isPropertyOf = foi
        noforest_NDVI.isObservedBy = [sent_sensor]
        forest_NDVI.isObservedBy = [sent_sensor]
        observation.observedProperty.append(noforest_NDVI)
        observation.observedProperty.append(forest_NDVI)
        
        ### MSAVI
        noforest_MSAVI = onto.mean_NDSI(row['image_name'][:-4]+row['DateTime'][0:10]+'_mean_noforest_MSAVI')
        forest_MSAVI = onto.mean_NDSI(row['image_name'][:-4]+row['DateTime'][0:10]+'_mean_forest_MSAVI')
        
        noforest_MSAVI.hasValue = row['MeanNoForestMSAVI']
        forest_MSAVI.hasValue = row['MeanForestMSAVI']
        noforest_MSAVI.isPropertyOf = foi
        forest_MSAVI.isPropertyOf = foi
        noforest_MSAVI.isObservedBy = [sent_sensor]
        forest_MSAVI.isObservedBy = [sent_sensor]
        observation.observedProperty.append(noforest_MSAVI)
        observation.observedProperty.append(forest_MSAVI)


        noforest_perc.hasMean = [noforest_NDVI, noforest_MSAVI]
        forest_perc.hasMean = [forest_NDVI, forest_MSAVI]

        
        c +=1
    else:
        pass

'''onto.save(file = "C:/Users/Giacomo/Desktop/ontology/SORSpopulated.owl", format = "rdfxml")
wh_ont.save(file = "C:/Users/Giacomo/Desktop/ontology/WeatherOntology1.owl", format = "rdfxml")
sosa.save(file = "C:/Users/Giacomo/Desktop/ontology/sosa1.owl", format = "rdfxml")
time.save(file = "C:/Users/Giacomo/Desktop/ontology/time1.owl", format = "rdfxml")'''