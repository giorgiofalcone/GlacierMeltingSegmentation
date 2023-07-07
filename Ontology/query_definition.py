# In this file all the queries realized for the SORS Platform are reported
# N.B. A lot of other queries can be made on SORS Ontology, but here are reported only the util ones.

from owlready2 import *


def query_on_ground(img_name, onto_class):
    '''
    This method makes a query to obtain information on 
    clean  classified areas.
    
    params:
        - img_name: a string containing the image file name
        - onto_class: a class of the ontology that represents the type of the Result we want
                    (At the moment it can assume three values: SORS.CleanPercentage, SORS.DebrisPercentage and SORS.TerrainPercentage)
    returns: 
        - result (a list containing all the information)
    '''
    
    result = list(default_world.sparql("""
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX time: <http://www.w3.org/2006/time#>
        PREFIX Weat: <https://www.auto.tuwien.ac.at/downloads/thinkhome/ontology/WeatherOntology.owl#>
        PREFIX : <http://example.org/SORSontology#>

        SELECT ?Perc ?meanNDVI_ent ?MeanNDVI ?meanNDSI ?meanNDWI_ent ?MeanNDWI ?meanElev_ent ?MeanElev ?MeanSlope 
        WHERE { 	?img :hasName ??1 .
            ?Res sosa:isResultOf ?img .
            ?Res rdf:type ??2 . 
            ?Res Weat:hasValue ?value;
                :hasMean ?meanNDVI_ent ;
                :hasMean ?meanNDSI_ent ;
                :hasMean ?meanNDWI_ent ;
                :hasMean ?meanElev_ent ;
                :hasMean ?meanSlope_ent .
            ?meanNDVI_ent rdf:type :mean_NDVI ;
                Weat:hasValue ?meanNDVI .
            ?meanNDSI_ent rdf:type :mean_NDSI ;
                Weat:hasValue ?meanNDSI.
            ?meanNDWI_ent rdf:type :mean_NDWI ;
                Weat:hasValue ?meanNDWI.
            ?meanElev_ent rdf:type :mean_elevation ;
                Weat:hasValue ?meanElev.
            ?meanSlope_ent rdf:type :mean_slope ;
                Weat:hasValue ?meanSlope.
            BIND ( STR(?value) as ?Perc )
            BIND ( STR(?meanNDVI) as ?MeanNDVI )
            BIND ( STR(?meanNDSI) as ?MeanNDSI )
            BIND ( STR(?meanNDWI) as ?MeanNDWI )
            BIND ( STR(?meanElev) as ?MeanElev )
            BIND ( STR(?meanSlope) as ?MeanSlope )
        }
    """, [img_name, onto_class]))
    return result



def query_on_ground_forest(img_name, onto_class):
    '''
    This method makes a query to obtain information on 
    clean  classified areas.
    
    params:
        - img_name: a string containing the image file name
        - onto_class: a class of the ontology that represents the type of the Result we want
                    (At the moment it can assume three values: SORS.CleanPercentage, SORS.DebrisPercentage and SORS.TerrainPercentage)
    returns: 
        - result (a list containing all the information)
    '''
    
    result = list(default_world.sparql("""
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX time: <http://www.w3.org/2006/time#>
        PREFIX Weat: <https://www.auto.tuwien.ac.at/downloads/thinkhome/ontology/WeatherOntology.owl#>
        PREFIX : <http://example.org/SORSontology#>

        SELECT ?Perc ?meanNDVI_ent ?MeanNDVI ?meanMSAVI_ent ?MeanMSAVI
        WHERE { 	?img :hasName ??1 .
            ?Res sosa:isResultOf ?img .
            ?Res rdf:type ??2 . 
            ?Res Weat:hasValue ?value;
                :hasMean ?meanNDVI_ent ;
                :hasMean ?meanMSAVI_ent .
            ?meanNDVI_ent rdf:type :mean_NDVI ;
                Weat:hasValue ?meanNDVI .
            ?meanMSAVI_ent rdf:type :mean_MSAVI ;
                Weat:hasValue ?meanMSAVI.
            BIND ( STR(?value) as ?Perc )
            BIND ( STR(?meanNDVI) as ?MeanNDVI )
            BIND ( STR(?meanMSAVI) as ?MeanMSAVI )
        }
    """, [img_name, onto_class]))
    return result



def query_on_temperature(img_name):
    '''
    This method makes a query to obtain information on 
    an area's temperature.
    
    params:
        - img_name: a string containing the image file name
    returns: : 
        - result (a list containing all the information)
    '''

    result = list(default_world.sparql("""
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX time: <http://www.w3.org/2006/time#>
        PREFIX Weat: <https://www.auto.tuwien.ac.at/downloads/thinkhome/ontology/WeatherOntology.owl#>
        PREFIX : <http://example.org/SORSontology#>

        SELECT ?ws ?avgTemp_ent ?AVG ?MAX ?MIN
        WHERE { 	?img :hasName ?? .
            ?ws :refersTo ?img .
            ?ws Weat:hasWeatherPhenomenon ?avgTemp_ent,
                                    ?maxTemp_ent,
                                    ?minTemp_ent .
            ?avgTemp_ent rdf:type :AvgTemperature ;
                Weat:hasValue ?avg .
            ?maxTemp_ent rdf:type :MaxTemperature ;
                Weat:hasValue ?max .
            ?minTemp_ent rdf:type :MinTemperature ;
                Weat:hasValue ?min .
            BIND ( STR(?avg) as ?AVG )
            BIND ( STR(?max) as ?MAX )
            BIND ( STR(?min) as ?MIN )
        }
    """, [img_name]))
    return result


def query_on_weather(img_name):
    '''
    This method makes a query to obtain information on 
    an area's temperature and precipitation.
    
    params:
        - img_name: a string containing the image file name
    returns: : 
        - result (a list containing all the information)
    '''

    result = list(default_world.sparql("""
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX time: <http://www.w3.org/2006/time#>
        PREFIX Weat: <https://www.auto.tuwien.ac.at/downloads/thinkhome/ontology/WeatherOntology.owl#>
        PREFIX : <http://example.org/SORSontology#>

        SELECT ?ws ?avgTemp_ent ?AVG ?MAX ?MIN ?rain_ent ?RAIN
        WHERE { 	?img :hasName ?? .
            ?ws :refersTo ?img .
            ?ws Weat:hasWeatherPhenomenon ?avgTemp_ent,
                                    ?maxTemp_ent,
                                    ?minTemp_ent,
                                    ?rain_ent .
            ?avgTemp_ent rdf:type :AvgTemperature ;
                Weat:hasValue ?avg .
            ?maxTemp_ent rdf:type :MaxTemperature ;
                Weat:hasValue ?max .
            ?minTemp_ent rdf:type :MinTemperature ;
                Weat:hasValue ?min .
            ?rain_ent rdf:type Weat:Precipitation ;
                Weat:hasIntensity ?rain .
            BIND ( STR(?avg) as ?AVG )
            BIND ( STR(?max) as ?MAX )
            BIND ( STR(?min) as ?MIN )
            BIND ( STR(?rain) as ?RAIN )
        }
    """, [img_name]))
    return result


def query_on_country(country):
    '''
    This method makes a query to obtain information on 
    images of a specific country.
    
    params:
        - country: a string containing the country of interest
    returns: 
        - result (a list containing all the information)
    '''

    result = list(default_world.sparql("""
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX time: <http://www.w3.org/2006/time#>
        PREFIX Weat: <https://www.auto.tuwien.ac.at/downloads/thinkhome/ontology/WeatherOntology.owl#>
        PREFIX : <http://example.org/SORSontology#>

        SELECT ?Name ?Lat ?Long ?Date
        WHERE { ?img :hasName ?name ;
                    :hasLat ?lat ;
	                :hasLong ?long ;
	                :hasLocation ?? ;
	                Weat:hasObservationTime ?date_ent.
	        ?date_ent :hasDate ?date.
            BIND ( STR(?name) as ?Name )
            BIND ( STR(?lat) as ?Lat )
            BIND ( STR(?long) as ?Long )
            BIND ( STR(?date) as ?Date )
        }
        
    """, [country]))
    return result