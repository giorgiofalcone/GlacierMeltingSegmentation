from owlready2 import *
import owlready2
from query_definition import *
import numpy as np
import earthpy.plot as ep
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# Load the ontology with imported ontologies
onto_path.append("C:/Users/giorg/OneDrive/Desktop/ontology_2/")
onto = get_ontology("http://example.org/SORSontology").load()
sosa = onto.imported_ontologies[0]
wh_ont = onto.imported_ontologies[1]
time = wh_ont.imported_ontologies[0]

# Activate reasoner
owlready2.JAVA_EXE = "C:\\Program Files\\Java\\jre1.8.0_341\\bin\\java.exe"

with onto:
    sync_reasoner_pellet([onto, sosa, wh_ont, time],infer_property_values = True)

# Execute first query on the ontology
country = 'Tajikistan'
location_query_result = query_on_country(country) #Il paese deve essere passato come parametro dalla selezione dell'utente della finestra a tendina.


''' Dopo questa prima query bisogna mostrare a video nome, data e coordinate
 delle immagini risultanti dalla query e l'utente dovrà selezionarne una.'''

# After selecting a specific image, saves its information
i = 0
if len(location_query_result) != 0:
    img_name = location_query_result[i][0]  #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)
    latitude = location_query_result[i][1]  #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)
    longitude = location_query_result[i][2] #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)
    date = location_query_result[i][3]      #Il primo indice dipende dalla scelta dell'utente tra le immagini disponibili (deve essere parametrizzato)

    ''' qui va caricata nella pagina l'immagine rgb e l'immagine segmentata che corrispondono a img_name'''

    inp_np = np.load('C:/Users/giorg/OneDrive/Desktop/ontology_2/Ontology_population/images/'+img_name)
    orig_img = np.dstack((inp_np[...,2],inp_np[...,1],inp_np[...,0]))
    image2 = orig_img.transpose(2,0,1)
    ep.plot_rgb(image2,
                title="RGB Composite Image",
                stretch=True,
                str_clip=1)

    img = mpimg.imread('C:/Users/giorg/OneDrive/Desktop/ontology_2/Ontology_population/segmentation/'+img_name.replace("npy","png"))
    plt.imshow(img)
    plt.show()

else:
    print('There are no observation for this country')


# Execute other queries on the specific image to obtain related info in the following order
# ?Perc ?meanNDVI_ent ?MeanNDVI ?meanNDSI ?meanNDWI_ent ?MeanNDWI ?meanElev_ent ?MeanElev ?MeanSlope 
ice_query_result = query_on_ground(img_name, onto.CleanIcePercentage)
debris_query_result = query_on_ground(img_name, onto.DebrisPercentage)
background_query_result = query_on_ground(img_name, onto.TerrainPercentage)

if len(ice_query_result) != 0 and len(debris_query_result) != 0 and len(background_query_result) != 0:
    ice_perc = round(float(ice_query_result[0][0])*100, 2)
    ice_NDVI_ent = ice_query_result[0][1]
    ice_NDVI = ice_query_result[0][2]
    ice_NDSI = ice_query_result[0][3]
    ice_NDWI_ent = ice_query_result[0][4]
    ice_NDWI = ice_query_result[0][5]
    ice_elev_ent = ice_query_result[0][6]
    ice_elev = round(float(ice_query_result[0][7]), 1)
    ice_slope = ice_query_result[0][8]

    debris_perc = round(float(debris_query_result[0][0])*100, 2)
    debris_NDVI_ent = debris_query_result[0][1]
    debris_NDVI = debris_query_result[0][2]
    debris_NDSI = debris_query_result[0][3]
    debris_NDWI_ent = debris_query_result[0][4]
    debris_NDWI = debris_query_result[0][5]
    debris_elev_ent = debris_query_result[0][6]
    debris_elev = round(float(debris_query_result[0][7]), 1)
    debris_slope = debris_query_result[0][8]

    back_perc = round(float(background_query_result[0][0])*100, 2)
    back_NDVI_ent = background_query_result[0][1]
    back_NDVI = background_query_result[0][2]
    back_NDSI = background_query_result[0][3]
    back_NDWI_ent = background_query_result[0][4]
    back_NDWI = background_query_result[0][5]
    back_elev_ent = background_query_result[0][6]
    back_elev = round(float(background_query_result[0][7]), 1)
    back_slope = background_query_result[0][8]
else:
    ice_perc = 'Unknown'
    ice_NDVI_ent = 'Unknown'
    ice_NDVI = 'Unknown'
    ice_NDSI = 'Unknown'
    ice_NDWI_ent = 'Unknown'
    ice_NDWI = 'Unknown'
    ice_elev_ent = 'Unknown'
    ice_elev = 'Unknown'
    ice_slope = 'Unknown'

    debris_perc = 'Unknown'
    debris_NDVI_ent = 'Unknown'
    debris_NDVI = 'Unknown'
    debris_NDSI = 'Unknown'
    debris_NDWI_ent = 'Unknown'
    debris_NDWI = 'Unknown'
    debris_elev_ent = 'Unknown'
    debris_elev = 'Unknown'
    debris_slope = 'Unknown'

    back_perc = 'Unknown'
    back_NDVI_ent = 'Unknown'
    back_NDVI = 'Unknown'
    back_NDSI = 'Unknown'
    back_NDWI_ent = 'Unknown'
    back_NDWI = 'Unknown'
    back_elev_ent = 'Unknown'
    back_elev = 'Unknown'
    back_slope = 'Unknown'

''' I dati salvati dalle 3 query precedenti verranno usati per 
    riempire la tabella nell'interfaccia '''

# Execute another query on the specific image to obtain info to temperature in the following order
# ?ws ?AVG ?MAX ?MIN
weather_query_result = query_on_temperature(img_name)

if len(weather_query_result) != 0:
    weather_ent = weather_query_result[0][0]
    avg_temp_ent = weather_query_result[0][1]
    avg_temp = round(float(weather_query_result[0][2]), 2)
    max_temp = round(float(weather_query_result[0][3]), 2)
    min_temp = round(float(weather_query_result[0][4]), 2)
else:
    weather_ent = 'Unknown'
    avg_temp_ent = 'Unknown'
    avg_temp = 'Unknown'
    max_temp = 'Unknown'
    min_temp = 'Unknown'

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
        wh_analysis_result = wh_analysis_result + f'and the weather state is classified as {conc}.\n'   
    else:
        wh_analysis_result = wh_analysis_result + f'but the wather state is not classified as a specific weather.\n'
else:
    wh_analysis_result = f'There are no weather information.\n'    

print(wh_analysis_result)



# Compute analysis on clean ice class
ice_analysis_result = ''
ice_no_mount = False
ice_low_mount = False
ice_rug_mount = False
ice_high_mount = False
ice_summit = False

if ice_perc != 'Unknown':
    ice_analysis_result = ice_analysis_result + f'This zone, at this date, have a Clean Ice percentage of about {ice_perc}%.\n'
    if onto.NoWaterOrBrightnessSurface in ice_NDWI_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has no presence of water or a brightness surface, since the average NDWI is {ice_NDWI}, '
    elif onto.ModeratePresenceOfWater in ice_NDWI_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has a moderate presence of water, since the average NDWI is {ice_NDWI}, '
    elif onto.HighPresenceOfWater in ice_NDWI_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has a high presence of water, since the average NDWI is {ice_NDWI}, '
    else:
        ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has an average NDWI of {ice_NDWI}.\n'
    
    if onto.NoMountain in ice_elev_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'and a mean elevation of {ice_elev} meters, which classifies the zone as a not mountainous area.\n'
        ice_no_mount = True
    elif onto.LowMountain in ice_elev_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'and a mean elevation of {ice_elev} meters, which classifies the zone as a Low Mountain area.\n'
        ice_low_mount = True
    elif onto.RuggedMountain in ice_elev_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'and a mean elevation of {ice_elev} meters, which classifies the zone as a Rugged Mountain area.\n'
        ice_rug_mount = True
    elif onto.HighMountain in ice_elev_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'and a mean elevation of {ice_elev} meters, which classifies the zone as a High Mountain area.\n'
        ice_high_mount = True
    elif onto.Summit in ice_elev_ent.is_a:
        ice_analysis_result = ice_analysis_result + f'and a mean elevation of {ice_elev} meters, which classifies the zone as a Summit.\n'
        ice_summit = True
    else:
        ice_analysis_result = ice_analysis_result + f'and a mean elevation of {ice_elev} meters.\n'
else:
    ice_analysis_result = f'There are no information about Clean Ice class.\n'

# Compute analysis on debris class
debris_analysis_result = ''
if debris_perc != 'Unknown':
    debris_analysis_result = debris_analysis_result + f'This zone, at this date, have a Debris covered Ice percentage of about {debris_perc}%.\n'
    if onto.NoWaterOrBrightnessSurface in debris_NDWI_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has no presence of water or a brightness surface, since the average NDWI is {debris_NDWI}, '
    elif onto.ModeratePresenceOfWater in debris_NDWI_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has a moderate presence of water, since the average NDWI is {debris_NDWI}, '
    elif onto.HighPresenceOfWater in debris_NDWI_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has a high presence of water, since the average NDWI is {debris_NDWI}, '
    else:
        debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has an average NDWI of {debris_NDWI}, '

    if onto.NoMountain in debris_elev_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'and a mean elevation of {debris_elev} meters, which classifies the zone as a not mountainous area.\n'
    elif onto.LowMountain in debris_elev_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'and a mean elevation of {debris_elev} meters, which classifies the zone as a Low Mountain area.\n'
    elif onto.RuggedMountain in debris_elev_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'and a mean elevation of {debris_elev} meters, which classifies the zone as a Rugged Mountain area.\n'
    elif onto.HighMountain in debris_elev_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'and a mean elevation of {debris_elev} meters, which classifies the zone as a High Mountain area.\n'
    elif onto.Summit in debris_elev_ent.is_a:
        debris_analysis_result = debris_analysis_result + f'and a mean elevation of {debris_elev} meters, which classifies the zone as a Summit.\n'
    else:
        debris_analysis_result = debris_analysis_result + f'and a mean elevation of {debris_elev} meters.\n'
else:
    debris_analysis_result = f'There are no information about Debris covered Ice class.\n'

# Compute analysis on background class
background_analysis_result = ''
if back_perc != 'Unknown':
    background_analysis_result = background_analysis_result + f'This zone, at this date, have a No-Ice percentage of about {back_perc}%.\n'
    if onto.NoWaterOrBrightnessSurface in back_NDWI_ent.is_a:
        background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has no presence of water or a brightness surface, since the average NDWI is {back_NDWI}, '
    elif onto.ModeratePresenceOfWater in back_NDWI_ent.is_a:
        background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has a moderate presence of water, since the average NDWI is {back_NDWI}, '
    elif onto.HighPresenceOfWater in back_NDWI_ent.is_a:
        background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has a high presence of water since, the average NDWI is {back_NDWI}, '
    else:
        background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has an average NDWI of {back_NDWI}, '

    if onto.NoMountain in back_elev_ent.is_a:
        background_analysis_result = background_analysis_result + f'and a mean elevation of {back_elev} meters, which classifies the zone as a not mountainous area.\n'
    elif onto.LowMountain in back_elev_ent.is_a:
        background_analysis_result = background_analysis_result + f'and a mean elevation of {back_elev} meters, which classifies the zone as a Low Mountain area.\n'
    elif onto.RuggedMountain in back_elev_ent.is_a:
        background_analysis_result = background_analysis_result + f'and a mean elevation of {back_elev} meters, which classifies the zone as a Rugged Mountain area.\n'
    elif onto.HighMountain in back_elev_ent.is_a:
        background_analysis_result = background_analysis_result + f'and a mean elevation of {back_elev} meters, which classifies the zone as a High Mountain area.\n'
    elif onto.Summit in back_elev_ent.is_a:
        background_analysis_result = background_analysis_result + f'and a mean elevation of {back_elev} meters, which classifies the zone as a Summit.\n'
    else:
        background_analysis_result = background_analysis_result + f'and a mean elevation of {back_elev} meters.\n'
else:
    background_analysis_result = f'There are no information about No-Ice class.\n'


print(ice_analysis_result)
print(debris_analysis_result)
print(background_analysis_result)


# Final Analysis
final_analysis = f''

if heating_ws or severe_ws:
    final_analysis = final_analysis + f"At the end, this observation is taken in critical conditions, since the average temperature, at a mean elevation of {ice_elev} meters, is {avg_temp}°C, reaching a maximum of {max_temp}°C. So this area has to be kept under observation to monitor glaciers melting."
elif cooling_ws:
    if broom and (ice_high_mount or ice_summit or ice_rug_mount):
        final_analysis = final_analysis + f"At the end, this observation is taken in warning conditions, since the average temperature, at a mean elevation of {ice_elev} meters, is {avg_temp}°C. So this area has to be kept under observation in the same period to monitor glaciers melting."
    elif abzero:
        final_analysis = final_analysis + f"At the end, this observation is taken in quite good conditions to avoid glaciers melting, since the average temperature, at a mean elevation of {ice_elev} meters, is {avg_temp}°C."
    elif bzero or frost or exfrost:
        final_analysis = final_analysis + f"At the end, this observation is taken in optimal conditions to avoid glaciers melting, since the average temperature, at a mean elevation of {ice_elev} meters, is {avg_temp}°C. These conditions ensure the glacier safety."
    else:
        final_analysis = final_analysis + f"At the end, this observation hasn't relevant features for glaciers monitoring, since there are not glaciers in this zone."
else:
    final_analysis = final_analysis + f"There are not enough informations about weather conditions to make a final consideration."

print(final_analysis)