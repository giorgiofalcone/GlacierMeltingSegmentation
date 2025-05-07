from re import I
from tkinter import image_names
from owlready2 import *
import owlready2
from query_definition import *
import tifffile
import matplotlib.pyplot as plt
import earthpy.plot as ep
import numpy as np
import matplotlib.image as mpimg

# Load the ontology with imported ontologies
onto_path.append("C:/Users/Giacomo/Desktop/ontology/")
onto = get_ontology("http://example.org/SORSontology").load()
sosa = onto.imported_ontologies[0]
wh_ont = onto.imported_ontologies[1]
time = wh_ont.imported_ontologies[0]

# Activate reasoner
owlready2.JAVA_EXE = "C:\\Program Files\\Java\\jre1.8.0_341\\bin\\java.exe"

with onto:
    sync_reasoner_pellet([onto, sosa, wh_ont, time],infer_property_values = True)

# Execute first query on the ontology
country = 'Aripuanã, State of Mato Grosso, Brazil'
location_query_result = query_on_country(country) #Il paese deve essere passato come parametro dalla selezione dell'utente della finestra a tendina.


''' Dopo questa prima query bisogna mostrare a video nome, data e coordinate
 delle immagini risultanti dalla query e l'utente dovrà selezionarne una.'''

# After selecting a specific image, saves its information
i=1
if len(location_query_result) != 0:
    img_name = location_query_result[i][0]  #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)
    latitude = location_query_result[i][1]  #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)
    longitude = location_query_result[i][2] #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)
    date = location_query_result[i][3]      #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)

    ''' qui va caricata nella pagina l'immagine rgb e l'immagine segmentata che corrispondono a img_name'''
    img=tifffile.imread('C:/Users/Giacomo/Desktop/ontology/ontology_population/images/'+img_name)
    image = np.dstack((img[...,0],img[...,1],img[...,2]))

    image2 = image.transpose(2,0,1)
    ep.plot_rgb(image2,
                title="RGB Composite Image",
                stretch=True,
                str_clip=1)

    pred = mpimg.imread('C:/Users/Giacomo/Desktop/ontology/ontology_population/segmentation/'+img_name.replace('tif','png'))
    plt.imshow(pred)
    plt.show()

else:
    print('There are no observation for this country')


# Execute other queries on the specific image to obtain related info in the following order
# ?Perc ?meanNDVI_ent ?MeanNDVI ?meanMSAVI_ent ?MeanMSAVI 
noforest_query_result = query_on_ground(img_name, onto.NoForestPercentage)
forest_query_result = query_on_ground(img_name, onto.ForestPercentage)

if len(noforest_query_result) != 0 and len(forest_query_result) != 0:
    noforest_perc = round(float(noforest_query_result[0][0])*100, 2)
    noforest_NDVI_ent = noforest_query_result[0][1]
    noforest_NDVI = noforest_query_result[0][2]
    noforest_MSAVI_ent = noforest_query_result[0][3]
    noforest_MSAVI = noforest_query_result[0][4]

    forest_perc = round(float(forest_query_result[0][0])*100, 2)
    forest_NDVI_ent = forest_query_result[0][1]
    forest_NDVI = forest_query_result[0][2]
    forest_MSAVI_ent = forest_query_result[0][3]
    forest_MSAVI = forest_query_result[0][4]
else:
    noforest_perc = 'Unknown'
    noforest_NDVI_ent = 'Unknown'
    noforest_NDVI = 'Unknown'
    noforest_MSAVI_ent = 'Unknown'
    noforest_MSAVI = 'Unknown'

    forest_perc = 'Unknown'
    forest_NDVI_ent = 'Unknown'
    forest_NDVI = 'Unknown'
    forest_MSAVI_ent = 'Unknown'
    forest_MSAVI = 'Unknown'

''' I dati salvati dalle 3 query precedenti verranno usati per 
    riempire la tabella nell'interfaccia '''

# Execute another query on the specific image to obtain info to weather in the following order
# ?ws ?avgTemp_ent ?AVG ?MAX ?MIN ?rain_ent ?RAIN
weather_query_result = query_on_weather(img_name)

if len(weather_query_result) != 0:
    weather_ent = weather_query_result[0][0]
    avg_temp_ent = weather_query_result[0][1]
    avg_temp = round(float(weather_query_result[0][2]), 2)
    max_temp = round(float(weather_query_result[0][3]), 2)
    min_temp = round(float(weather_query_result[0][4]), 2)
    rain_ent = weather_query_result[0][5]
    rain = round(float(weather_query_result[0][6]), 2)
else:
    weather_ent = 'Unknown'
    avg_temp_ent = 'Unknown'
    avg_temp = 'Unknown'
    max_temp = 'Unknown'
    min_temp = 'Unknown'
    rain_ent = 'Unknown'
    rain = 'Unknown'

''' Queste informazioni verranno stampate a video dopo la tabella (oppure dentro ma devono occupare una sola colonna)'''


### Compute a qualitative analysis on data from ontology obtained also through reasoning
# Weather analysis
wh_analysis_result = f''

# Setting some flags
exfrost = False
frost = False
bzero = False
abzero = False
broom = False
room = False
abroom = False
heat = False
exheat = False

w_state = list()
cooling_ws = False
heating_ws = False
rainy_ws = False
severe_ws = False

if weather_ent != 'Unknown':
    # Compute analysis on temperature
    wh_analysis_result = wh_analysis_result + f"""The satellite image is taken in {date}, {country}, at coordinates [{latitude}, {longitude}].\nIn this day, at these coordinates, a maximum temperature of {max_temp}°C and a minimum temperature of {min_temp}°C are reached.\nMeanwhile, the average temperature all over the day is {avg_temp}°C"""
    if wh_ont.ExtremeFrost in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as an Extreme Frost temperature '
        exfrost = True
    elif wh_ont.Frost in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as a Frost temperature '
        frost = True
    elif wh_ont.BelowOrZeroTemperature in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as a Below or Zero temperature '
        bzero = True
    elif wh_ont.AboveZeroTemperature in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as an Above Zero temperature '
        abzero = True
    elif wh_ont.BelowRoomTemperature in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as a temperature Below Room temperature '
        broom = True
    elif wh_ont.RoomTemperature in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as a Room temperature '
        room = True
    elif wh_ont.AboveRoomTemperature in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as a temperature Above Room temperature '
        abroom = True
    elif wh_ont.Heat in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as a Heat temperature '
        heat = True
    elif wh_ont.Heat in avg_temp_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', so it is classified as an Extreme Heat temperature '
        exheat = True
    else: 
        pass

    # Compute analysis on Precipitation
    wh_analysis_result = wh_analysis_result + f"""and a total precipitation of {rain} mm is registered"""
    if wh_ont.NoPrecipitation in rain_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', characterizing this day as a without precipitation day. '
    elif wh_ont.LightPrecipitation in rain_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', characterizing this day with light precipitations. '
    elif wh_ont.ModeratePrecipitation in rain_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', characterizing this day with moderate precipitations. '
    elif wh_ont.HeavyPrecipitation in rain_ent.is_a:
        wh_analysis_result = wh_analysis_result + f', characterizing this day with heavy precipitations. '
    else:
        pass

    # Compute analysis on Weather State
    if wh_ont.CoolingWeatherState in weather_ent.is_a:
        w_state.append('Cooling Weather')
        cooling_ws = True
    if wh_ont.HeatingWeatherState in weather_ent.is_a:
        w_state.append('Heating Weather')
        heating_ws = True
    if wh_ont.RainyWeatherState in weather_ent.is_a:
        w_state.append('Rainy Weather')
        rainy_ws = True
    if wh_ont.SevereWeatherState in weather_ent.is_a:
        w_state.append('Severe Weather')
        severe_ws = True
    if len(w_state) != 0:
        conc = ''
        for x in w_state:
            conc = conc + x + ', '
        conc = conc[:-2]
        wh_analysis_result = wh_analysis_result + f'The weather state is classified as {conc}.\n'   
    else:
        wh_analysis_result = wh_analysis_result + f'The wather state is not classified as a specific weather.\n'
else:
    wh_analysis_result = f'There are no weather information.\n'    

print(wh_analysis_result)


# Compute analysis on no forest class
noforest_analysis_result = ''

noveg_nf = False
lowveg_nf = False
medveg_nf = False
highveg_nf = False

if noforest_perc != 'Unknown':
    noforest_analysis_result = noforest_analysis_result + f'This zone, at this date, have a no forest percentage of about {noforest_perc}%.\n'
    
    # NDVI
    if onto.NoVegetation in noforest_NDVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has no presence of vegetation, since the average NDVI is {noforest_NDVI}, '
        noveg_nf = True
    elif onto.LowVegetationVigor in noforest_NDVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has a vegetation with a low vigor, since the average NDVI is {noforest_NDVI}, '
        lowveg_nf = True
    elif onto.MediumVegetationVigor in noforest_NDVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has a vegetation with a medium vigor, since the average NDVI is {noforest_NDVI}, '
        medveg_nf = True
    elif onto.HighVegetationVigor in noforest_NDVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has a vegetation with a high vigor, since the average NDVI is {noforest_NDVI}, '
        highveg_nf = True
    else:
        noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has an average NDVI of {noforest_NDVI}, '
    
    # MSAVI
    if onto.BareSoil in noforest_MSAVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'and this area is classified has bare soil, since the average MSAVI is {noforest_MSAVI}.\n'
    elif onto.LeafDevelopmentStage in noforest_MSAVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'and the vegetation in this area is in a leaf development stage, since the average MSAVI is {noforest_MSAVI}.\n'
    elif onto.DenseVegetation in noforest_MSAVI_ent.is_a:
        noforest_analysis_result = noforest_analysis_result + f'and the vegetation in this area is dense, since the average MSAVI is {noforest_MSAVI}.\n'
    else:
        noforest_analysis_result = noforest_analysis_result + f'and has an average MSAVI of {noforest_MSAVI}.\n'
else:
    noforest_analysis_result = f'There are no information about no forest class.\n'


# Compute analysis on forest class
forest_analysis_result = ''

noveg = False
lowveg = False
medveg = False
highveg = False

if forest_perc != 'Unknown':
    forest_analysis_result = forest_analysis_result + f'This zone, at this date, have a forest percentage of about {forest_perc}%.\n'
    
    # NDVI
    if onto.NoVegetation in forest_NDVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has no presence of vegetation, since the average NDVI is {forest_NDVI}, '
        noveg = True
    elif onto.LowVegetationVigor in forest_NDVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has a vegetation with a low vigor, since the average NDVI is {forest_NDVI}, '
        lowveg = True
    elif onto.MediumVegetationVigor in forest_NDVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has a vegetation with a medium vigor, since the average NDVI is {forest_NDVI}, '
        medveg = True
    elif onto.HighVegetationVigor in forest_NDVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has a vegetation with a high vigor, since the average NDVI is {forest_NDVI}, '
        highveg = True
    else:
        forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has an average NDVI of {forest_NDVI}, '
    
    # MSAVI
    if onto.BareSoil in forest_MSAVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'and this area is classified has bare soil, since the average MSAVI is {forest_MSAVI}.\n'
    elif onto.LeafDevelopmentStage in forest_MSAVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'and the vegetation in this area is in a leaf development stage, since the average MSAVI is {forest_MSAVI}.\n'
    elif onto.DenseVegetation in forest_MSAVI_ent.is_a:
        forest_analysis_result = forest_analysis_result + f'and the vegetation in this area is dense, since the average MSAVI is {forest_MSAVI}.\n'
    else:
        forest_analysis_result = forest_analysis_result + f'and has an average MSAVI of {forest_MSAVI}.\n'
else:
    forest_analysis_result = f'There are no information about forest class.\n'

print(noforest_analysis_result)
print(forest_analysis_result)


# Final Analysis
forest_final_analysis = f''

if heating_ws:
    if heat or exheat:
        if not rainy_ws and (noveg or lowveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in critical conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations and the vegetation vigor is very low: this situation can lead to fires."
        elif not rainy_ws and (medveg or highveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in critical conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations: this situation can lead to fires, even though vegetation vigor is high."
        elif rainy_ws and (noveg or lowveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is not risky for fires, since even though the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C and the vegetation vigor is quite low, there are precipitations."
        elif rainy_ws and (medveg or highveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is not risky for fires, since even though the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are precipitations and the vegetation vigor is quite high."
    elif abroom:
        if not rainy_ws and (noveg or lowveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in warning conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations and the vegetation vigor is very low: this situation could lead to fires."
        elif not rainy_ws and (medveg or highveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in warning conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations: this situation could lead to fires, even though vegetation vigor is high."
        elif rainy_ws and (noveg or lowveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in good conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C and there are precipitations, but the vegetation vigor is quite low."
        elif rainy_ws and (medveg or highveg):
            forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in optimal conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are precipitations and the vegetation vigor is medium-high."
    else:
        forest_final_analysis = forest_final_analysis + f"This observation in the forest area,  is characterized by heating weather."
else:
    if noveg or lowveg:
        forest_final_analysis = forest_final_analysis + f"In forest areas, the vegetation vigor is very low."
    elif medveg or highveg:
        forest_final_analysis = forest_final_analysis + f"In forest areas, the vegetation vigor is medium-high."
    else:
        forest_final_analysis = forest_final_analysis + f"There are not enough informations about this forest area to make a final consideration."


no_forest_final_analysis = f''

if heating_ws:
    if heat or exheat:
        if not rainy_ws and (noveg_nf or lowveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in critical conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations and the vegetation vigor is very low: this situation can lead to fires."
        elif not rainy_ws and (medveg_nf or highveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in critical conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations: this situation can lead to fires, even though vegetation vigor is high."
        elif rainy_ws and (noveg_nf or lowveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is not risky for fires, since even though the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C and the vegetation vigor is quite low, there are precipitations."
        elif rainy_ws and (medveg_nf or highveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is not risky for fires, since even though the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are precipitations and the vegetation vigor is quite high."
    elif abroom:
        if not rainy_ws and (noveg_nf or lowveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in warning conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations and the vegetation vigor is very low: this situation could lead to fires."
        elif not rainy_ws and (medveg_nf or highveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in warning conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are no precipitations: this situation could lead to fires, even though vegetation vigor is high."
        elif rainy_ws and (noveg_nf or lowveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in good conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C and there are precipitations, but the vegetation vigor is quite low."
        elif rainy_ws and (medveg_nf or highveg_nf):
            no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in optimal conditions, since the average temperature is {avg_temp}°C, reaching a maximum of {max_temp}°C, there are precipitations and the vegetation vigor is medium-high."
    else:
        no_forest_final_analysis = no_forest_final_analysis + f"This observation in the non forest area, is characterized by heating weather."
else:
    if noveg_nf or lowveg_nf:
        no_forest_final_analysis = no_forest_final_analysis + f"In no forest areas, the vegetation vigor is very low."
    elif medveg_nf or highveg_nf:
        no_forest_final_analysis = no_forest_final_analysis + f"In no forest areas, the vegetation vigor is medium-high."
    else:
        no_forest_final_analysis = no_forest_final_analysis + f"There are not enough informations about this no forest area to make a final consideration."

print(forest_final_analysis)
print(no_forest_final_analysis)
