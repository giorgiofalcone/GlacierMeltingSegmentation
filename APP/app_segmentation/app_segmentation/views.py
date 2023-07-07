from http.client import HTTPResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from app_segmentation.models import *
import tempfile

import yaml
import torch
import numpy as np
import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from addict import Dict
from app_segmentation.glacier_mapping.models.frame import Framework
from app_segmentation.glacier_mapping.models.metrics import diceloss
import matplotlib.patches as mpatches

from sklearn.preprocessing import minmax_scale

from owlready2 import *
import owlready2
from app_segmentation.query_definition import *
import numpy as np
import earthpy.plot as ep
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import tifffile
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


# Load the ontology with imported ontologies
onto_path.append("app_segmentation/fusion/")

onto = get_ontology("http://example.org/SORSontology").load()
sosa = onto.imported_ontologies[0]
wh_ont = onto.imported_ontologies[1]
time = wh_ont.imported_ontologies[0]

# Activate reasoner
owlready2.JAVA_EXE = "C:\\Program Files\\Java\\jre1.8.0_341\\bin\\java.exe"

with onto:
    sync_reasoner_pellet([onto, sosa, wh_ont, time],infer_property_values = True)


conf = Dict(yaml.safe_load(open("app_segmentation/train.yaml", "r")))
conf_forest = Dict(yaml.safe_load(open("app_segmentation/train_fpn_forest.yaml", "r")))
device = torch.device('cpu')

model_dir = f"app_segmentation/model_best.pt"
model_dir_forest = f"app_segmentation/model_best_forest.pt"

outchannels = conf.model_opts.args.classes
outchannels_forest = conf_forest.model_opts.args.classes

if outchannels > 1:
    loss_weight = [1 for _ in range(outchannels)]
    loss_weight[-1] = 0 # background
    loss_fn = diceloss(act=torch.nn.Softmax(dim=1), w=loss_weight,
                               outchannels=outchannels)
else:
    loss_fn = diceloss()

frame = Framework(
    model_opts=conf.model_opts,
    optimizer_opts=conf.optim_opts,
    reg_opts=conf.reg_opts,
    loss_fn=loss_fn,
    device=device
)
    
net = frame.model
net.load_state_dict(torch.load(model_dir, map_location=torch.device('cpu')))#, map_location=torch.device('cpu')
net = net.to(device)

if outchannels_forest > 1:
    loss_weight_forest = [1 for _ in range(outchannels_forest)]
    loss_weight_forest[-1] = 0 # background
    loss_fn_forest = diceloss(act=torch.nn.Softmax(dim=1), w=loss_weight_forest,
                               outchannels=outchannels_forest)
else:
    loss_fn_forest = diceloss()

frame_forest = Framework(
    model_opts=conf_forest.model_opts,
    optimizer_opts=conf_forest.optim_opts,
    reg_opts=conf_forest.reg_opts,
    loss_fn=loss_fn_forest,
    device=device
)
    
net_forest = frame_forest.model
net_forest.load_state_dict(torch.load(model_dir_forest, map_location=torch.device('cpu')))#, map_location=torch.device('cpu')
net_forest = net_forest.to(device)

def index(request):
    template = loader.get_template('Start.html')
    return HttpResponse(template.render())

def home(request):
    template = loader.get_template('Home.html')
    return HttpResponse(template.render())

def home_forest(request):
    template = loader.get_template('Home_forest.html')
    return HttpResponse(template.render())

def handle_uploaded_file(f):
    with open(f"app_segmentation/templates/saved_images/{f.name}", 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def upload(request):
    if request.method == "GET":
        return HttpResponse(render(request, 'Upload.html', {}))

    handle_uploaded_file(request.FILES['file'])

    image = Image()
    image.location = request.POST.get('location')
    image.date = request.POST.get('date')
    image.name = request.FILES['file'].name
    image.save()

    return HttpResponseRedirect(f'/visualize?id={image.id}')


def upload_forest(request):
    if request.method == "GET":
        return HttpResponse(render(request, 'Upload_forest.html', {}))

    handle_uploaded_file(request.FILES['file'])

    image = Image()
    image.location = request.POST.get('location')
    image.date = request.POST.get('date')
    image.name = request.FILES['file'].name
    image.save()

    return HttpResponseRedirect(f'/visualize_forest?id={image.id}')



def img_info(request):
    img_name = request.GET.get('img_name').replace('.png', '.npy')
    req = request.GET.get('opt').split(';')
    date = req[2].split(':')[1]
    latitude = req[1].split(':')[1].split(',')[0].replace('(','')
    longitude = req[1].split(':')[1].split(',')[1].replace(')','')
    
    data = {}

    # Execute other queries on the specific image to obtain related info in the following order
    # ?Perc ?meanNDVI_ent ?MeanNDVI ?meanNDSI ?meanNDWI_ent ?MeanNDWI ?meanElev_ent ?MeanElev ?MeanSlope 
    ice_query_result = query_on_ground(img_name, onto.CleanIcePercentage)
    debris_query_result = query_on_ground(img_name, onto.DebrisPercentage)
    background_query_result = query_on_ground(img_name, onto.TerrainPercentage)

    if len(ice_query_result) != 0 and len(debris_query_result) != 0 and len(background_query_result) != 0:
        data['ice_perc'] = str(round(float(ice_query_result[0][0])*100, 2)) + ' %'
        ice_NDVI_ent = ice_query_result[0][1]
        data['ice_NDVI'] = ice_query_result[0][2]
        data['ice_NDSI'] = ice_query_result[0][3]
        ice_NDWI_ent = ice_query_result[0][4]
        data['ice_NDWI'] = ice_query_result[0][5]
        ice_elev_ent = ice_query_result[0][6]
        data['ice_elev'] = round(float(ice_query_result[0][7]), 1)
        data['ice_slope'] = ice_query_result[0][8]

        data['debris_perc'] =  str(round(float(debris_query_result[0][0])*100, 2)) + ' %'
        debris_NDVI_ent = debris_query_result[0][1]
        data['debris_NDVI'] = debris_query_result[0][2]
        data['debris_NDSI'] = debris_query_result[0][3]
        debris_NDWI_ent = debris_query_result[0][4]
        data['debris_NDWI'] = debris_query_result[0][5]
        debris_elev_ent = debris_query_result[0][6]
        data['debris_elev'] = round(float(debris_query_result[0][7]), 1)
        data['debris_slope'] = debris_query_result[0][8]

        data['back_perc'] = str(round(float(background_query_result[0][0])*100, 2)) + ' %'
        back_NDVI_ent = background_query_result[0][1]
        data['back_NDVI'] = background_query_result[0][2]
        data['back_NDSI'] = background_query_result[0][3]
        back_NDWI_ent = background_query_result[0][4]
        data['back_NDWI'] = background_query_result[0][5]
        back_elev_ent = background_query_result[0][6]
        data['back_elev'] = round(float(background_query_result[0][7]), 1)
        data['back_slope'] = background_query_result[0][8]
    else:
        data['ice_perc'] = 'Unknown'
        ice_NDVI_ent = 'Unknown'
        data['ice_NDVI'] = 'Unknown'
        data['ice_NDSI'] = 'Unknown'
        ice_NDWI_ent = 'Unknown'
        data['ice_NDWI'] = 'Unknown'
        ice_elev_ent = 'Unknown'
        data['ice_elev'] = 'Unknown'
        data['ice_slope'] = 'Unknown'

        data['debris_perc'] = 'Unknown'
        debris_NDVI_ent = 'Unknown'
        data['debris_NDVI'] = 'Unknown'
        data['debris_NDSI'] = 'Unknown'
        debris_NDWI_ent = 'Unknown'
        data['debris_NDWI'] = 'Unknown'
        debris_elev_ent = 'Unknown'
        data['debris_elev'] = 'Unknown'
        data['debris_slope']= 'Unknown'

        data['back_perc'] = 'Unknown'
        back_NDVI_ent = 'Unknown'
        data['back_NDVI'] = 'Unknown'
        data['back_NDSI'] = 'Unknown'
        back_NDWI_ent = 'Unknown'
        data['back_NDWI'] = 'Unknown'
        back_elev_ent = 'Unknown'
        data['back_elev'] = 'Unknown'
        data['back_slope'] = 'Unknown'


    # Execute another query on the specific image to obtain info to temperature in the following order
    # ?ws ?AVG ?MAX ?MIN
    weather_query_result = query_on_temperature(img_name)

    if len(weather_query_result) != 0:
        weather_ent = weather_query_result[0][0]
        avg_temp_ent= weather_query_result[0][1]
        data['avg_temp'] = str(round(float(weather_query_result[0][2]), 2)) + ' °C'
        data['max_temp'] = str(round(float(weather_query_result[0][3]), 2)) + ' °C'
        data['min_temp']= str(round(float(weather_query_result[0][4]), 2)) + ' °C'
    else:
        weather_ent = 'Unknown'
        avg_temp_ent = 'Unknown'
        data['avg_temp'] = 'Unknown'
        data['max_temp'] = 'Unknown'
        data['min_temp'] = 'Unknown'

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
        wh_analysis_result = wh_analysis_result + f"""The satellite image is taken in {date}, at coordinates [{latitude}, {longitude}].\nIn this day, at these coordinates, a maximum temperature of {data["max_temp"]} and a minimum temperature of {data["min_temp"]} are reached.\nMeanwhile, the average temperature all over the day is {data["avg_temp"]}"""
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


    data['wh_analysis_result'] = wh_analysis_result

    # Compute analysis on clean ice class
    ice_analysis_result = ''
    ice_no_mount = False
    ice_low_mount = False
    ice_rug_mount = False
    ice_high_mount = False
    ice_summit = False

    if data['ice_perc'] != 'Unknown':
        ice_analysis_result = ice_analysis_result + f'This zone, at this date, have a Clean Ice percentage of about {data["ice_perc"]}.\n'
        if onto.NoWaterOrBrightnessSurface in ice_NDWI_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has no presence of water or a brightness surface, since the average NDWI is {data["ice_NDWI"]}, '
        elif onto.ModeratePresenceOfWater in ice_NDWI_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has a moderate presence of water, since the average NDWI is {data["ice_NDWI"]}, '
        elif onto.HighPresenceOfWater in ice_NDWI_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has a high presence of water, since the average NDWI is {data["ice_NDWI"]}, '
        else:
            ice_analysis_result = ice_analysis_result + f'This Observation, in the Clean Ice areas, has an average NDWI of {data["ice_NDWI"]}.\n'
        
        if onto.NoMountain in ice_elev_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'and a mean elevation of {data["ice_elev"]} meters, which classifies the zone as a not mountainous area.\n'
            ice_no_mount = True
        elif onto.LowMountain in ice_elev_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'and a mean elevation of {data["ice_elev"]} meters, which classifies the zone as a Low Mountain area.\n'
            ice_low_mount = True
        elif onto.RuggedMountain in ice_elev_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'and a mean elevation of {data["ice_elev"]} meters, which classifies the zone as a Rugged Mountain area.\n'
            ice_rug_mount = True
        elif onto.HighMountain in ice_elev_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'and a mean elevation of {data["ice_elev"]} meters, which classifies the zone as a High Mountain area.\n'
            ice_high_mount = True
        elif onto.Summit in ice_elev_ent.is_a:
            ice_analysis_result = ice_analysis_result + f'and a mean elevation of {data["ice_elev"]} meters, which classifies the zone as a Summit.\n'
            ice_summit = True
        else:
            ice_analysis_result = ice_analysis_result + f'and a mean elevation of {data["ice_elev"]} meters.\n'
    else:
        ice_analysis_result = f'There are no information about Clean Ice class.\n'

    # Compute analysis on debris class
    debris_analysis_result = ''
    if data['debris_perc'] != 'Unknown':
        debris_analysis_result = debris_analysis_result + f'This zone, at this date, have a Debris covered Ice percentage of about {data["debris_perc"]}.\n'
        if onto.NoWaterOrBrightnessSurface in debris_NDWI_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has no presence of water or a brightness surface, since the average NDWI is {data["debris_NDWI"]}, '
        elif onto.ModeratePresenceOfWater in debris_NDWI_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has a moderate presence of water, since the average NDWI is {data["debris_NDWI"]}, '
        elif onto.HighPresenceOfWater in debris_NDWI_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has a high presence of water, since the average NDWI is {data["debris_NDWI"]}, '
        else:
            debris_analysis_result = debris_analysis_result + f'This Observation, in the Debris Covered Ice areas, has an average NDWI of {data["debris_NDWI"]}, '

        if onto.NoMountain in debris_elev_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'and a mean elevation of {data["debris_elev"]} meters, which classifies the zone as a not mountainous area.\n'
        elif onto.LowMountain in debris_elev_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'and a mean elevation of {data["debris_elev"]} meters, which classifies the zone as a Low Mountain area.\n'
        elif onto.RuggedMountain in debris_elev_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'and a mean elevation of {data["debris_elev"]} meters, which classifies the zone as a Rugged Mountain area.\n'
        elif onto.HighMountain in debris_elev_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'and a mean elevation of {data["debris_elev"]} meters, which classifies the zone as a High Mountain area.\n'
        elif onto.Summit in debris_elev_ent.is_a:
            debris_analysis_result = debris_analysis_result + f'and a mean elevation of {data["debris_elev"]} meters, which classifies the zone as a Summit.\n'
        else:
            debris_analysis_result = debris_analysis_result + f'and a mean elevation of {data["debris_elev"]} meters.\n'
    else:
        debris_analysis_result = f'There are no information about Debris covered Ice class.\n'

    # Compute analysis on background class
    background_analysis_result = ''
    if data["back_perc"] != 'Unknown':
        background_analysis_result = background_analysis_result + f'This zone, at this date, have a No-Ice percentage of about {data["back_perc"]}.\n'
        if onto.NoWaterOrBrightnessSurface in back_NDWI_ent.is_a:
            background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has no presence of water or a brightness surface, since the average NDWI is {data["back_NDWI"]}, '
        elif onto.ModeratePresenceOfWater in back_NDWI_ent.is_a:
            background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has a moderate presence of water, since the average NDWI is {data["back_NDWI"]}, '
        elif onto.HighPresenceOfWater in back_NDWI_ent.is_a:
            background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has a high presence of water since, the average NDWI is {data["back_NDWI"]}, '
        else:
            background_analysis_result = background_analysis_result + f'This Observation, in the Background areas, has an average NDWI of {data["back_NDWI"]}, '

        if onto.NoMountain in back_elev_ent.is_a:
            background_analysis_result = background_analysis_result + f'and a mean elevation of {data["back_elev"]} meters, which classifies the zone as a not mountainous area.\n'
        elif onto.LowMountain in back_elev_ent.is_a:
            background_analysis_result = background_analysis_result + f'and a mean elevation of {data["back_elev"]} meters, which classifies the zone as a Low Mountain area.\n'
        elif onto.RuggedMountain in back_elev_ent.is_a:
            background_analysis_result = background_analysis_result + f'and a mean elevation of {data["back_elev"]} meters, which classifies the zone as a Rugged Mountain area.\n'
        elif onto.HighMountain in back_elev_ent.is_a:
            background_analysis_result = background_analysis_result + f'and a mean elevation of {data["back_elev"]} meters, which classifies the zone as a High Mountain area.\n'
        elif onto.Summit in back_elev_ent.is_a:
            background_analysis_result = background_analysis_result + f'and a mean elevation of {data["back_elev"]} meters, which classifies the zone as a Summit.\n'
        else:
            background_analysis_result = background_analysis_result + f'and a mean elevation of {data["back_elev"]} meters.\n'
    else:
        background_analysis_result = f'There are no information about No-Ice class.\n'


    data['ice_analysis_result'] = ice_analysis_result
    data['debris_analysis_result'] = debris_analysis_result
    data['background_analysis_result'] = background_analysis_result


    # Final Analysis
    final_analysis = f''

    if heating_ws or severe_ws:
        final_analysis = final_analysis + f"At the end, this observation is taken in critical conditions, since the average temperature, at a mean elevation of {data['ice_elev']} meters, is {data['avg_temp']}, reaching a maximum of {data['max_temp']}. So this area has to be kept under observation to monitor glaciers melting."
    elif cooling_ws:
        if broom and (ice_high_mount or ice_summit or ice_rug_mount):
            final_analysis = final_analysis + f"At the end, this observation is taken in warning conditions, since the average temperature, at a mean elevation of {data['ice_elev']} meters, is {data['avg_temp']}. So this area has to be kept under observation in the same period to monitor glaciers melting."
        elif abzero:
            final_analysis = final_analysis + f"At the end, this observation is taken in quite good conditions to avoid glaciers melting, since the average temperature, at a mean elevation of {data['ice_elev']} meters, is {data['avg_temp']}."
        elif bzero or frost or exfrost:
            final_analysis = final_analysis + f"At the end, this observation is taken in optimal conditions to avoid glaciers melting, since the average temperature, at a mean elevation of {data['ice_elev']} meters, is {data['avg_temp']}. These conditions ensure the glacier safety."
        else:
            final_analysis = final_analysis + f"At the end, this observation hasn't relevant features for glaciers monitoring, since there are not glaciers in this zone."
    else:
        final_analysis = final_analysis + f"There are not enough informations about weather conditions to make a final consideration."

    data['final_analysis'] = final_analysis

    return HttpResponse(json.dumps(data))




def knowledge_base(request):
    if request.method == "GET":
        template = loader.get_template('Knowledge-Base.html')
        return HttpResponse(template.render())
    
    country = request.GET.get('country')
    
    location_query_result = query_on_country(country) 

    images = []
    for record in location_query_result:
        images.append({
            'img_name':record[0].replace(".npy", '.png'),
            'latitude':record[1],
            'longitude': record[2],
            'date':record[3]
        })
    return HttpResponse(json.dumps(images))




def knowledge_base_forest(request):
    if request.method == "GET":
        template = loader.get_template('Knowledge-Base_forest.html')
        return HttpResponse(template.render())
    
    country = request.GET.get('country')
    
    location_query_result = query_on_country(country) 

    images = []
    for record in location_query_result:
        images.append({
            'img_name':record[0].replace(".tif", '.png'),
            'latitude':record[1],
            'longitude': record[2],
            'date':record[3]
        })
    return HttpResponse(json.dumps(images))


def img_info_forest(request):
    img_name = request.GET.get('img_name').replace('.png', '.tif')
    req = request.GET.get('opt').split(';')
    date = req[2].split(':')[1]
    latitude = req[1].split(':')[1].split(',')[0].replace('(','')
    longitude = req[1].split(':')[1].split(',')[1].replace(')','')
    data = {}

    # Execute other queries on the specific image to obtain related info in the following order
    # ?Perc ?meanNDVI_ent ?MeanNDVI ?meanNDSI ?meanNDWI_ent ?MeanNDWI ?meanElev_ent ?MeanElev ?MeanSlope 
    noforest_query_result = query_on_ground_forest(img_name, onto.NoForestPercentage)
    forest_query_result = query_on_ground_forest(img_name, onto.ForestPercentage)
    
    
    if len(noforest_query_result) != 0 and len(forest_query_result):
        data['noforest_perc'] = str(round(float(noforest_query_result[0][0])*100, 2)) + ' %'
        noforest_NDVI_ent = noforest_query_result[0][1]
        data['noforest_NDVI'] = noforest_query_result[0][2]
        noforest_MSAVI_ent = noforest_query_result[0][3]
        data['noforest_MSAVI'] = noforest_query_result[0][4]

        data['forest_perc'] =  str(round(float(forest_query_result[0][0])*100, 2)) + ' %'
        forest_NDVI_ent = forest_query_result[0][1]
        data['forest_NDVI'] = forest_query_result[0][2]
        forest_MSAVI_ent = forest_query_result[0][3]
        data['forest_MSAVI'] = forest_query_result[0][4]
    else:
        data['noforest_perc'] = 'Unknown'
        noforest_NDVI_ent = 'Unknown'
        data['noforest_NDVI'] = 'Unknown'
        noforest_MSAVI_ent = 'Unknown'
        data['noforest_MSAVI'] = 'Unknown'
        
        data['forest_perc'] =  'Unknown'
        forest_NDVI_ent = 'Unknown'
        data['forest_NDVI'] = 'Unknown'
        forest_MSAVI_ent = 'Unknown'
        data['forest_MSAVI'] = 'Unknown'
        

    # Execute another query on the specific image to obtain info to temperature in the following order
    weather_query_result = query_on_weather(img_name)
    
    if len(weather_query_result) != 0:
        weather_ent = weather_query_result[0][0]
        avg_temp_ent= weather_query_result[0][1]
        data['avg_temp'] = str(round(float(weather_query_result[0][2]), 2)) + ' °C'
        data['max_temp'] = str(round(float(weather_query_result[0][3]), 2)) + ' °C'
        data['min_temp']= str(round(float(weather_query_result[0][4]), 2)) + ' °C'
        rain_ent = weather_query_result[0][5]
        data['rain'] = str(round(float(weather_query_result[0][6]), 2)) + ' mm'
    else:
        weather_ent = 'Unknown'
        avg_temp_ent = 'Unknown'
        data['avg_temp'] = 'Unknown'
        data['max_temp'] = 'Unknown'
        data['min_temp'] = 'Unknown'
        rain_ent = 'Unknown'
        data['rain'] = 'Unknown'


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
        wh_analysis_result = wh_analysis_result + f"""The satellite image is taken in {date}, at coordinates [{latitude}, {longitude}].\nIn this day, at these coordinates, a maximum temperature of {data['max_temp']} and a minimum temperature of {data['min_temp']} are reached.\nMeanwhile, the average temperature all over the day is {data['avg_temp']}"""
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
        wh_analysis_result = wh_analysis_result + f"""and a total precipitation of {data['rain']} is registered"""
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

    data['wh_analysis_result'] = wh_analysis_result


    # Compute analysis on no forest class
    noforest_analysis_result = ''

    noveg_nf = False
    lowveg_nf = False
    medveg_nf = False
    highveg_nf = False

    if data['noforest_perc'] != 'Unknown':
        noforest_analysis_result = noforest_analysis_result + f'This zone, at this date, have a no forest percentage of about {data["noforest_perc"]}.\n'
        
        # NDVI
        if onto.NoVegetation in noforest_NDVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has no presence of vegetation, since the average NDVI is {data["noforest_NDVI"]}, '
            noveg_nf = True
        elif onto.LowVegetationVigor in noforest_NDVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has a vegetation with a low vigor, since the average NDVI is {data["noforest_NDVI"]}, '
            lowveg_nf = True
        elif onto.MediumVegetationVigor in noforest_NDVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has a vegetation with a medium vigor, since the average NDVI is {data["noforest_NDVI"]}, '
            medveg_nf = True
        elif onto.HighVegetationVigor in noforest_NDVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has a vegetation with a high vigor, since the average NDVI is {data["noforest_NDVI"]}, '
            highveg_nf = True
        else:
            noforest_analysis_result = noforest_analysis_result + f'This Observation, in no forest areas, has an average NDVI of {data["noforest_NDVI"]}, '
        
        # MSAVI
        if onto.BareSoil in noforest_MSAVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'and this area is classified has bare soil, since the average MSAVI is {data["noforest_MSAVI"]}.\n'
        elif onto.LeafDevelopmentStage in noforest_MSAVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'and the vegetation in this area is in a leaf development stage, since the average MSAVI is {data["noforest_MSAVI"]}.\n'
        elif onto.DenseVegetation in noforest_MSAVI_ent.is_a:
            noforest_analysis_result = noforest_analysis_result + f'and the vegetation in this area is dense, since the average MSAVI is {data["noforest_MSAVI"]}.\n'
        else:
            noforest_analysis_result = noforest_analysis_result + f'and has an average MSAVI of {data["noforest_MSAVI"]}.\n'
    else:
        noforest_analysis_result = f'There are no information about no forest class.\n'

    # Compute analysis on forest class
    forest_analysis_result = ''

    noveg = False
    lowveg = False
    medveg = False
    highveg = False

    if data["forest_perc"] != 'Unknown':
        forest_analysis_result = forest_analysis_result + f'This zone, at this date, have a forest percentage of about {data["forest_perc"]}.\n'
        
        # NDVI
        if onto.NoVegetation in forest_NDVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has no presence of vegetation, since the average NDVI is {data["forest_NDVI"]}, '
            noveg = True
        elif onto.LowVegetationVigor in forest_NDVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has a vegetation with a low vigor, since the average NDVI is {data["forest_NDVI"]}, '
            lowveg = True
        elif onto.MediumVegetationVigor in forest_NDVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has a vegetation with a medium vigor, since the average NDVI is {data["forest_NDVI"]}, '
            medveg = True
        elif onto.HighVegetationVigor in forest_NDVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has a vegetation with a high vigor, since the average NDVI is {data["forest_NDVI"]}, '
            highveg = True
        else:
            forest_analysis_result = forest_analysis_result + f'This Observation, in forest areas, has an average NDVI of {data["forest_NDVI"]}, '
        
        # MSAVI
        if onto.BareSoil in forest_MSAVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'and this area is classified has bare soil, since the average MSAVI is {data["forest_MSAVI"]}.\n'
        elif onto.LeafDevelopmentStage in forest_MSAVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'and the vegetation in this area is in a leaf development stage, since the average MSAVI is {data["forest_MSAVI"]}.\n'
        elif onto.DenseVegetation in forest_MSAVI_ent.is_a:
            forest_analysis_result = forest_analysis_result + f'and the vegetation in this area is dense, since the average MSAVI is {data["forest_MSAVI"]}.\n'
        else:
            forest_analysis_result = forest_analysis_result + f'and has an average MSAVI of {data["forest_MSAVI"]}.\n'
    else:
        forest_analysis_result = f'There are no information about forest class.\n'
    

    data['noforest_analysis_result'] = noforest_analysis_result
    data['forest_analysis_result'] = forest_analysis_result


    # Final Analysis
    forest_final_analysis = f''

    if heating_ws:
        if heat or exheat:
            if not rainy_ws and (noveg or lowveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in critical conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations and the vegetation vigor is very low: this situation can lead to fires."
            elif not rainy_ws and (medveg or highveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in critical conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations: this situation can lead to fires, even though vegetation vigor is high."
            elif rainy_ws and (noveg or lowveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is not risky for fires, since even though the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']} and the vegetation vigor is quite low, there are precipitations."
            elif rainy_ws and (medveg or highveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is not risky for fires, since even though the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are precipitations and the vegetation vigor is quite high."
        elif abroom:
            if not rainy_ws and (noveg or lowveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in warning conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations and the vegetation vigor is very low: this situation could lead to fires."
            elif not rainy_ws and (medveg or highveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in warning conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations: this situation could lead to fires, even though vegetation vigor is high."
            elif rainy_ws and (noveg or lowveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in good conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']} and there are precipitations, but the vegetation vigor is quite low."
            elif rainy_ws and (medveg or highveg):
                forest_final_analysis = forest_final_analysis + f"At the end, this observation in the forest area, is taken in optimal conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are precipitations and the vegetation vigor is medium-high."
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
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in critical conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations and the vegetation vigor is very low: this situation can lead to fires."
            elif not rainy_ws and (medveg_nf or highveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in critical conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations: this situation can lead to fires, even though vegetation vigor is high."
            elif rainy_ws and (noveg_nf or lowveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is not risky for fires, since even though the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']} and the vegetation vigor is quite low, there are precipitations."
            elif rainy_ws and (medveg_nf or highveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is not risky for fires, since even though the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are precipitations and the vegetation vigor is quite high."
        elif abroom:
            if not rainy_ws and (noveg_nf or lowveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in warning conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations and the vegetation vigor is very low: this situation could lead to fires."
            elif not rainy_ws and (medveg_nf or highveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in warning conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are no precipitations: this situation could lead to fires, even though vegetation vigor is high."
            elif rainy_ws and (noveg_nf or lowveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in good conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']} and there are precipitations, but the vegetation vigor is quite low."
            elif rainy_ws and (medveg_nf or highveg_nf):
                no_forest_final_analysis = no_forest_final_analysis + f"At the end, this observation in the non forest area, is taken in optimal conditions, since the average temperature is {data['avg_temp']}, reaching a maximum of {data['max_temp']}, there are precipitations and the vegetation vigor is medium-high."
        else:
            no_forest_final_analysis = no_forest_final_analysis + f"This observation in the non forest area, is characterized by heating weather."
    else:
        if noveg_nf or lowveg_nf:
            no_forest_final_analysis = no_forest_final_analysis + f"In no forest areas, the vegetation vigor is very low."
        elif medveg_nf or highveg_nf:
            no_forest_final_analysis = no_forest_final_analysis + f"In no forest areas, the vegetation vigor is medium-high."
        else:
            no_forest_final_analysis = no_forest_final_analysis + f"There are not enough informations about this no forest area to make a final consideration."

    data['forest_final_analysis'] = forest_final_analysis
    data['no_forest_final_analysis'] = no_forest_final_analysis

    return HttpResponse(json.dumps(data))




def visualize(request):
    image_id = request.GET.get('id')
    if image_id is None:
        return HttpResponseRedirect('/')
    image = Image.objects.get(id=image_id)

    img_dir = f"app_segmentation/templates/saved_images/{image.name}"
    with tempfile.TemporaryDirectory(dir='app_segmentation/templates/results') as temp_dir:
        pred_dir = f"{temp_dir}/segmentation/"
    if not os.path.exists(pred_dir):
        os.makedirs(pred_dir)

    ### Make and save prediction
    filename = image.name.split("/")[-1].replace("npy","png")
    #filename2 = image.name.split("/")[-1]
    inp_np = np.load(img_dir)
    nan_mask = np.isnan(inp_np[:,:,:9]).any(axis=2)
    inp_tensor = torch.from_numpy(np.expand_dims(np.transpose(inp_np, (2,0,1)), axis=0))
    inp_tensor = inp_tensor.to(device)
    output = net(inp_tensor)
    output_np = output.detach().cpu().numpy()
    output_np = np.transpose(output_np[0], (1,2,0))
    output_np = np.argmax(output_np, axis=2)
    output_np[nan_mask] = 3



    orig_img = np.dstack((inp_np[...,2],inp_np[...,1],inp_np[...,0]))
    image2 = orig_img.transpose(2,0,1)
    ep.plot_rgb(image2,
                title="RGB Composite Image",
                stretch=True,
                str_clip=1)
    plt.savefig(f"{pred_dir}{filename}")
    plt.close()



    ### To show the segmented image
    plt.imshow(output_np)

    ice = mpatches.Patch(color='#440154', label='Clean Ice')
    debris = mpatches.Patch(color='#208f8b', label='Debris Covered Ice')
    back = mpatches.Patch(color='#fde724', label='Background')

    plt.legend(handles=[ice, debris, back],loc="upper left")
    plt.savefig(f"{pred_dir}pred_{filename}")
    plt.close()

    static_img_file = pred_dir.replace('app_segmentation/templates', '/static') + filename
    static_pred_img_file = pred_dir.replace('app_segmentation/templates', '/static') + 'pred_' + filename

    ### Aggiungere info estratte dal post-processing
    ### Upload images and their prediction
    # Mean lists
    mean_ndvi_ice = list()
    mean_ndvi_debris = list()
    mean_ndvi_back = list()

    mean_ndsi_ice = list()
    mean_ndsi_debris = list()
    mean_ndsi_back = list()

    mean_ndwi_ice = list()
    mean_ndwi_debris = list()
    mean_ndwi_back = list()

    mean_slope_ice = list()
    mean_slope_debris = list()
    mean_slope_back = list()

    mean_elev_ice = list()
    mean_elev_debris = list()
    mean_elev_back = list()

    ice_perc = list()
    debris_perc = list()
    back_perc = list()

    # Indices dictionary
    mean_ndvi = dict()
    mean_ndsi = dict()
    mean_ndwi = dict()
    mean_slope = dict()
    mean_elevation = dict()
    percentage = dict()
    mean_ndvi = {0:mean_ndvi_ice,1:mean_ndvi_debris,2:mean_ndvi_back}
    mean_ndsi = {0:mean_ndsi_ice,1:mean_ndsi_debris,2:mean_ndsi_back}
    mean_ndwi = {0:mean_ndwi_ice,1:mean_ndwi_debris,2:mean_ndwi_back}
    mean_slope = {0:mean_slope_ice,1:mean_slope_debris,2:mean_slope_back}
    mean_elevation = {0:mean_elev_ice,1:mean_elev_debris,2:mean_elev_back}
    percentage = {0:ice_perc,1:debris_perc,2:back_perc}


    for glac_class in range(0,3):
        if glac_class == 0:
            mean_ndvi_ice.append(round(minmax_scale(inp_np[output_np==glac_class][:,10], feature_range=(-1, 1)).mean().item(),6))
            mean_ndsi_ice.append(round(minmax_scale(inp_np[output_np==glac_class][:,11], feature_range=(-1, 1)).mean().item(),6))
            mean_ndwi_ice.append(round(minmax_scale(inp_np[output_np==glac_class][:,12], feature_range=(-1, 1)).mean().item(),6))
            mean_elev_ice.append(round(minmax_scale(inp_np[output_np==glac_class][:,13], feature_range=(500, 8000)).mean().item(),6))
            mean_slope_ice.append(round(inp_np[output_np==glac_class][:,14].mean().item(),6))
            ice_perc.append(round((output_np == glac_class).sum()/(512*512),6))
            mean_ndvi[glac_class] = mean_ndvi_ice
            mean_ndsi[glac_class] = mean_ndsi_ice
            mean_ndwi[glac_class] = mean_ndwi_ice
            mean_elevation[glac_class] = mean_elev_ice
            mean_slope[glac_class] = mean_slope_ice
            percentage[glac_class] = ice_perc
        elif glac_class == 1:
            mean_ndvi_debris.append(round(minmax_scale(inp_np[output_np==glac_class][:,10], feature_range=(-1, 1)).mean().item(),6))
            mean_ndsi_debris.append(round(minmax_scale(inp_np[output_np==glac_class][:,11], feature_range=(-1, 1)).mean().item(),6))
            mean_ndwi_debris.append(round(minmax_scale(inp_np[output_np==glac_class][:,12], feature_range=(-1, 1)).mean().item(),6))
            mean_elev_debris.append(round(minmax_scale(inp_np[output_np==glac_class][:,13], feature_range=(500, 8000)).mean().item(),6))
            mean_slope_debris.append(round(inp_np[output_np==glac_class][:,14].mean().item(),6))
            debris_perc.append(round((output_np == glac_class).sum()/(512*512),6))
            mean_ndvi[glac_class] = mean_ndvi_debris
            mean_ndsi[glac_class] = mean_ndsi_debris
            mean_ndwi[glac_class] = mean_ndwi_debris
            mean_elevation[glac_class] = mean_elev_debris
            mean_slope[glac_class] = mean_slope_debris
            percentage[glac_class] = debris_perc
        else:
            mean_ndvi_back.append(round(minmax_scale(inp_np[output_np==glac_class][:,10], feature_range=(-1, 1)).mean().item(),6))
            mean_ndsi_back.append(round(minmax_scale(inp_np[output_np==glac_class][:,11], feature_range=(-1, 1)).mean().item(),6))
            mean_ndwi_back.append(round(minmax_scale(inp_np[output_np==glac_class][:,12], feature_range=(-1, 1)).mean().item(),6))
            mean_elev_back.append(round(minmax_scale(inp_np[output_np==glac_class][:,13], feature_range=(500, 8000)).mean().item(),6))
            mean_slope_back.append(round(inp_np[output_np==glac_class][:,14].mean().item(),6))
            back_perc.append(round((output_np == glac_class).sum()/(512*512),6))
            mean_ndvi[glac_class] = mean_ndvi_back
            mean_ndsi[glac_class] = mean_ndsi_back
            mean_ndwi[glac_class] = mean_ndwi_back
            mean_elevation[glac_class] = mean_elev_back
            mean_slope[glac_class] = mean_slope_back
            percentage[glac_class] = back_perc
        

    # Final dictionary
    mean_values = dict()
    mean_values['ndvi'] = mean_ndvi
    mean_values['ndsi'] = mean_ndsi
    mean_values['ndwi'] = mean_ndwi
    mean_values['slope'] = mean_slope
    mean_values['elevation'] = mean_elevation   
    mean_values['percentage'] = percentage 


    CleanIcePercentage = round(float(mean_values['percentage'][0][0])*100,2)
    DebrisIcePercentage = round(float(mean_values['percentage'][1][0])*100,2)
    BackgroundPercentage = round(float(mean_values['percentage'][2][0])*100,2)
    MeanIceNDVI = mean_values['ndvi'][0][0]
    MeanDebrisNDVI = mean_values['ndvi'][1][0]
    MeanBackgroundNDVI = mean_values['ndvi'][2][0]
    MeanIceNDSI = mean_values['ndsi'][0][0]
    MeanDebrisNDSI = mean_values['ndsi'][1][0]
    MeanBackgroundNDSI = mean_values['ndsi'][2][0]
    MeanIceNDWI = mean_values['ndwi'][0][0]
    MeanDebrisNDWI = mean_values['ndwi'][1][0]
    MeanBackgroundNDWI = mean_values['ndwi'][2][0]
    MeanIceElevation = round(float(mean_values['elevation'][0][0]),1)
    MeanDebrisElevation = round(float(mean_values['elevation'][1][0]),1)
    MeanBackgroundElevation = round(float(mean_values['elevation'][2][0]),1)
    MeanIceSlope = mean_values['slope'][0][0]
    MeanDebrisSlope = mean_values['slope'][1][0]
    MeanBackgroundSlope = mean_values['slope'][2][0]


    return HttpResponse(render(request, 'Visualize.html', {"img_file":static_img_file, "pred_img_file":static_pred_img_file, 'location': image.location, 'date': image.date,
    "CleanIcePercentage":CleanIcePercentage, "DebrisIcePercentage":DebrisIcePercentage, "BackgroundPercentage":BackgroundPercentage, "MeanIceNDVI":MeanIceNDVI,
    "MeanDebrisNDVI":MeanDebrisNDVI, "MeanBackgroundNDVI":MeanBackgroundNDVI, "MeanIceNDSI":MeanIceNDSI, "MeanDebrisNDSI":MeanDebrisNDSI, "MeanBackgroundNDSI":MeanBackgroundNDSI,
    "MeanIceNDWI":MeanIceNDWI, "MeanDebrisNDWI":MeanDebrisNDWI, "MeanBackgroundNDWI":MeanBackgroundNDWI, "MeanIceElevation":MeanIceElevation, "MeanDebrisElevation":MeanDebrisElevation,
    "MeanBackgroundElevation":MeanBackgroundElevation, "MeanIceSlope":MeanIceSlope, "MeanDebrisSlope":MeanDebrisSlope, "MeanBackgroundSlope":MeanBackgroundSlope}))





def visualize_forest(request):
    image_id = request.GET.get('id')
    if image_id is None:
        return HttpResponseRedirect('/home_forest')
    image = Image.objects.get(id=image_id)

    img_dir = f"app_segmentation/templates/saved_images/{image.name}"
    with tempfile.TemporaryDirectory(dir='app_segmentation/templates/results') as temp_dir:
        pred_dir = f"{temp_dir}/segmentation/"
    if not os.path.exists(pred_dir):
        os.makedirs(pred_dir)

    ### Make and save prediction
    filename = image.name.split("/")[-1].replace("tif","png")
    #filename2 = image.name.split("/")[-1].replace("tif","npy")

    img = tifffile.imread(img_dir).astype(np.float32)
    # Calcolo ndvi
    red = img[...,2]
    nir = img[...,3]
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)
    # Calcolo msavi
    msavi = nir.astype(float) + 0.5 - (0.5 * np.sqrt((2 * nir.astype(float) + 1)**2 - 8 * (nir.astype(float) - (2 * red.astype(float)))))
    image_tot = np.dstack((img, ndvi.astype(np.float32, order='C'), msavi.astype(np.float32, order='C')))

    inp_tensor=torch.from_numpy(np.expand_dims(image_tot,axis=0)).permute((0,3,1,2)).to(device)
    output = net_forest(inp_tensor)
    output_np = output.detach().cpu().numpy()
    output_np = np.transpose(output_np[0], (1,2,0))
    output_np = np.argmax(output_np, axis=2)


    orig_img = np.dstack((image_tot[...,0],image_tot[...,1],image_tot[...,2]))
    image2 = orig_img.transpose(2,0,1)
    ep.plot_rgb(image2,
                title="RGB Composite Image",
                stretch=True,
                str_clip=1)
    plt.savefig(f"{pred_dir}{filename}")
    plt.close()



    ### To show the segmented image
    plt.imshow(output_np)

    noforest = mpatches.Patch(color='#440154', label='No Forest')
    forest = mpatches.Patch(color='#fde724', label='Forest')

    plt.legend(handles=[noforest, forest],loc="upper left")
    plt.savefig(f"{pred_dir}pred_{filename}")
    plt.close()

    static_img_file = pred_dir.replace('app_segmentation/templates', '/static') + filename
    static_pred_img_file = pred_dir.replace('app_segmentation/templates', '/static') + 'pred_' + filename

    ### Aggiungere info estratte dal post-processing
    ### Upload images and their prediction
    # Mean lists
    mean_ndvi_forest = list()
    mean_ndvi_no_forest = list()

    mean_msavi_forest = list()
    mean_msavi_no_forest = list()

    forest_perc = list()
    no_forest_perc = list()

    # Indices dictionary
    mean_ndvi = dict()
    mean_msavi = dict()
    percentage = dict()
    mean_ndvi = {0:mean_ndvi_no_forest,1:mean_ndvi_forest}
    mean_msavi = {0:mean_msavi_no_forest,1:mean_msavi_forest}
    percentage = {0:no_forest_perc,1:forest_perc}


    for glac_class in range(0,2):
        if glac_class == 1:
            mean_ndvi_forest.append(round(image_tot[output_np==glac_class][:,4].mean().item(),6))
            mean_msavi_forest.append(round(image_tot[output_np==glac_class][:,5].mean().item(),6))
            forest_perc.append(round((output_np == glac_class).sum()/(512*512),6))
            mean_ndvi[glac_class] = mean_ndvi_forest
            mean_msavi[glac_class] = mean_msavi_forest
            percentage[glac_class] = forest_perc
        else:
            mean_ndvi_no_forest.append(round(image_tot[output_np==glac_class][:,4].mean().item(),6))
            mean_msavi_no_forest.append(round(image_tot[output_np==glac_class][:,5].mean().item(),6))
            no_forest_perc.append(round((output_np == glac_class).sum()/(512*512),6))
            mean_ndvi[glac_class] = mean_ndvi_no_forest
            mean_msavi[glac_class] = mean_msavi_no_forest
            percentage[glac_class] = no_forest_perc
        

    # Final dictionary
    mean_values = dict()
    mean_values['ndvi'] = mean_ndvi
    mean_values['msavi'] = mean_msavi
    mean_values['percentage'] = percentage


    NoForestPercentage = round(float(mean_values['percentage'][0][0])*100, 2)
    ForestPercentage = round(float(mean_values['percentage'][1][0])*100, 2)
    MeanNoForestNDVI = mean_values['ndvi'][0][0]
    MeanForestNDVI = mean_values['ndvi'][1][0]
    MeanNoForestMSAVI = mean_values['msavi'][0][0]
    MeanForestMSAVI = mean_values['msavi'][1][0]


    return HttpResponse(render(request, 'Visualize_forest.html', {"img_file":static_img_file, "pred_img_file":static_pred_img_file, 'location': image.location, 'date': image.date,
    "NoForestPercentage":NoForestPercentage, "ForestPercentage":ForestPercentage, "MeanNoForestNDVI":MeanNoForestNDVI, "MeanForestNDVI":MeanForestNDVI,
    "MeanNoForestMSAVI":MeanNoForestMSAVI, "MeanForestMSAVI":MeanForestMSAVI}))