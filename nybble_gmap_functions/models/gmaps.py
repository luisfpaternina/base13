# -*- coding: utf-8 -*-
import logging
import googlemaps
import numpy as np
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

def closest_node(node, nodes):
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)

#Dado un punto de inicio y distintos puntos, devuelve el punto mas lejano del punto de inicio
#Ejemplo punto_inicio: ["41.8855277,-87.6440611"]
#Ejemplo lista_puntos:  ["41.8848274,-87.6320859", "41.878729,-87.6301087", "41.8855277,-87.6440611"]
def distancia_mas_larga(api_key=False,punto_inicio=False,lista_puntos=False):
    punto_inicio=["41.8855277,-87.6440611"]
    lista_puntos=["41.8848274,-87.6320859", "41.878729,-87.6301087"]
#    gmaps = googlemaps.Client(key=api_key)    
    gmaps = googlemaps.Client(key='AIzaSyB3Ew41MBLuugjv5W7Zyq-_ablGcIFrQ4k')
    result=gmaps.distance_matrix(origins=punto_inicio, 
                        destinations=lista_puntos, 
                        departure_time=datetime.now() + timedelta(minutes=10))
    print('result:',result)
#    result={'destination_addresses': ['100 W Randolph St Uppr 101, Chicago, IL 60601, USA', '204 S Clark St, Chicago, IL 60604, USA'], 'origin_addresses': ['650 W Lake St, Chicago, IL 60661, USA'], 'rows': [{'elements': [{'distance': {'text': '1.4 km', 'value': 1414}, 'duration': {'text': '5 mins', 'value': 280}, 'duration_in_traffic': {'text': '5 mins', 'value': 327}, 'status': 'OK'}, {'distance': {'text': '1.8 km', 'value': 1846}, 'duration': {'text': '6 mins', 'value': 389}, 'duration_in_traffic': {'text': '7 mins', 'value': 427}, 'status': 'OK'}]}], 'status': 'OK'}
    if result['status']=='OK':
        elementos=result['rows'][0]['elements']
        distancias=[]
        index=0
        maximo=0
        for elemento in elementos:
            if elemento['distance']['value']>maximo:
                maximo=elemento['distance']['value']
            distancias.append(elemento['distance']['value'])
        index = distancias.index(maximo)
        return lista_puntos[index]



#Dado un punto de inicio A, un punto de fin B y distintos puntos, devuelve la ruta óptima de A a B
def mejor_ruta(api_key=False,punto_inicio=False,punto_fin=False,lista_puntos=False):
    #Mi depa
    punto_inicio="-24.772208,-65.405155"
    #Casa de mis abuelos, casa de mi tia alicia, casa koki
    lista_puntos=["-24.774446,-65.428997","-24.786493,-65.408791","-24.758196,-65.408256"]
    #Mi casa
    punto_fin="-24.772197,-65.433291"
#    gmaps = googlemaps.Client(key=api_key)
#    gmaps = googlemaps.Client(key='AIzaSyB3Ew41MBLuugjv5W7Zyq-_ablGcIFrQ4k')
#    results = gmaps.directions(origin = punto_inicio,
 #                                            destination = punto_fin,
  #                                           waypoints = lista_puntos,
   #                                          optimize_waypoints = True,
    #                                         departure_time=datetime.now() + timedelta(hours=1),
     #                                        mode='driving'
      #                                       )
    results=[{'bounds': {'northeast': {'lat': -24.7577148, 'lng': -65.4034724}, 'southwest': {'lat': -24.786619, 'lng': -65.4332895}}, 'copyrights': 'Map data ©2022', 'legs': [{'distance': {'text': '1.8 km', 'value': 1777}, 'duration': {'text': '4 mins', 'value': 243}, 'end_address': 'Ruiz Díaz de Guzmán 433, Salta, Argentina', 'end_location': {'lat': -24.758182, 'lng': -65.40826059999999}, 'start_address': 'Pueyrredón 1436, Salta, Argentina', 'start_location': {'lat': -24.7722089, 'lng': -65.4051448}, 'steps': [{'distance': {'text': '80 m', 'value': 80}, 'duration': {'text': '1 min', 'value': 11}, 'end_location': {'lat': -24.7714892, 'lng': -65.4050652}, 'html_instructions': 'Head <b>north</b> on <b>Pueyrredón</b> toward <b>Arenales</b>', 'polyline': {'points': 'hievCbmenKoCM'}, 'start_location': {'lat': -24.7722089, 'lng': -65.4051448}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.1 km', 'value': 140}, 'duration': {'text': '1 min', 'value': 25}, 'end_location': {'lat': -24.7713765, 'lng': -65.4064452}, 'html_instructions': 'Turn <b>left</b> at the 1st cross street onto <b>Arenales</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'xdevCtlenKItBE~@ARAb@Ad@'}, 'start_location': {'lat': -24.7714892, 'lng': -65.4050652}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '1.5 km', 'value': 1511}, 'duration': {'text': '3 mins', 'value': 195}, 'end_location': {'lat': -24.7580634, 'lng': -65.4078261}, 'html_instructions': '<b>Arenales</b> turns <b>right</b> and becomes <b>Deán Funes</b>', 'polyline': {'points': 'bdevChuenK}Fc@wFYwBMkAG{@CgCMqBIiBI}B?{BFmBNiBRqBd@A@oFhAqFnAsBd@}Bf@{Bf@wBh@'}, 'start_location': {'lat': -24.7713765, 'lng': -65.4064452}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '46 m', 'value': 46}, 'duration': {'text': '1 min', 'value': 12}, 'end_location': {'lat': -24.758182, 'lng': -65.40826059999999}, 'html_instructions': 'Turn <b>left</b> onto <b>Ruiz Díaz de Guzmán</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'zpbvC|}enKVtA'}, 'start_location': {'lat': -24.7580634, 'lng': -65.4078261}, 'travel_mode': 'DRIVING'}], 'traffic_speed_entry': [], 'via_waypoint': []}, {'distance': {'text': '3.7 km', 'value': 3694}, 'duration': {'text': '10 mins', 'value': 607}, 'end_address': 'Gral. Martin Güemes 456, Salta, Argentina', 'end_location': {'lat': -24.786531, 'lng': -65.4087961}, 'start_address': 'Ruiz Díaz de Guzmán 433, Salta, Argentina', 'start_location': {'lat': -24.758182, 'lng': -65.40826059999999}, 'steps': [{'distance': {'text': '0.2 km', 'value': 186}, 'duration': {'text': '1 min', 'value': 28}, 'end_location': {'lat': -24.7577148, 'lng': -65.4064918}, 'html_instructions': 'Head <b>east</b> on <b>Ruiz Díaz de Guzmán</b> toward <b>Deán Funes</b>', 'polyline': {'points': 'rqbvCr`fnKWuAc@mCa@}B'}, 'start_location': {'lat': -24.758182, 'lng': -65.40826059999999}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.7 km', 'value': 708}, 'duration': {'text': '2 mins', 'value': 107}, 'end_location': {'lat': -24.7638423, 'lng': -65.4045752}, 'html_instructions': 'Turn <b>right</b> at the 2nd cross street onto <b>Pueyrredón</b>', 'maneuver': 'turn-right', 'polyline': {'points': 'tnbvCpuenK~Bi@rBc@tBe@zBi@ZInEcArFmAbGcA'}, 'start_location': {'lat': -24.7577148, 'lng': -65.4064918}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.1 km', 'value': 114}, 'duration': {'text': '1 min', 'value': 18}, 'end_location': {'lat': -24.7637519, 'lng': -65.4034724}, 'html_instructions': 'Turn <b>left</b> onto <b>Juana Moro de López</b>', 'maneuver': 'turn-left', 'polyline': {'points': '~tcvCrienKCu@M}AKa@Jg@'}, 'start_location': {'lat': -24.7638423, 'lng': -65.4045752}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.9 km', 'value': 889}, 'duration': {'text': '2 mins', 'value': 112}, 'end_location': {'lat': -24.7714122, 'lng': -65.40598349999999}, 'html_instructions': 'Turn <b>right</b> onto <b>Pachi Gorriti</b>', 'maneuver': 'turn-right', 'polyline': {'points': 'ltcvCtbenKL@p@Nr@NJBpCn@jBb@rBb@bAVdATzBf@@?hCl@hCn@tFpAvFpA'}, 'start_location': {'lat': -24.7637519, 'lng': -65.4034724}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '10 m', 'value': 10}, 'duration': {'text': '1 min', 'value': 4}, 'end_location': {'lat': -24.7714006, 'lng': -65.40607779999999}, 'html_instructions': 'Turn <b>right</b> onto <b>Arenales</b>', 'maneuver': 'turn-right', 'polyline': {'points': 'hdevCjrenKAR'}, 'start_location': {'lat': -24.7714122, 'lng': -65.40598349999999}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '1.7 km', 'value': 1706}, 'duration': {'text': '5 mins', 'value': 309}, 'end_location': {'lat': -24.786619, 'lng': -65.4079962}, 'html_instructions': 'Turn <b>left</b> onto <b>Deán Funes</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'fdevC~renKtFpA\\DPBd@FfAFV@fAFdFXxFTzBL~BJ|FXxFXvFVR@nBJJ@zBLxFXlDPvAHvG^'}, 'start_location': {'lat': -24.7714006, 'lng': -65.40607779999999}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '81 m', 'value': 81}, 'duration': {'text': '1 min', 'value': 29}, 'end_location': {'lat': -24.786531, 'lng': -65.4087961}, 'html_instructions': 'Turn <b>right</b> onto <b>Gral. Martin Güemes</b><div style="font-size:0.9em">Destination will be on the right</div>', 'maneuver': 'turn-right', 'polyline': {'points': 'jchvC~~enKQ~C'}, 'start_location': {'lat': -24.786619, 'lng': -65.4079962}, 'travel_mode': 'DRIVING'}], 'traffic_speed_entry': [], 'via_waypoint': []}, {'distance': {'text': '3.5 km', 'value': 3519}, 'duration': {'text': '10 mins', 'value': 609}, 'end_address': 'Pedernera 1128, Salta, Argentina', 'end_location': {'lat': -24.7744445, 'lng': -65.4290176}, 'start_address': 'Gral. Martin Güemes 456, Salta, Argentina', 'start_location': {'lat': -24.786531, 'lng': -65.4087961}, 'steps': [{'distance': {'text': '0.3 km', 'value': 331}, 'duration': {'text': '1 min', 'value': 78}, 'end_location': {'lat': -24.786186, 'lng': -65.4120563}, 'html_instructions': 'Head <b>west</b> on <b>Gral. Martin Güemes</b> toward <b>Zuviria</b>', 'polyline': {'points': 'xbhvC~cfnKKlB]nGYlG'}, 'start_location': {'lat': -24.786531, 'lng': -65.4087961}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.6 km', 'value': 561}, 'duration': {'text': '2 mins', 'value': 122}, 'end_location': {'lat': -24.7811632, 'lng': -65.4115655}, 'html_instructions': 'Turn <b>right</b> at the 3rd cross street onto <b>Balcarce</b>', 'maneuver': 'turn-right', 'polyline': {'points': 't`hvCjxfnKcGW_GYK?iFYsFU'}, 'start_location': {'lat': -24.786186, 'lng': -65.4120563}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.6 km', 'value': 573}, 'duration': {'text': '2 mins', 'value': 121}, 'end_location': {'lat': -24.7806986, 'lng': -65.4171075}, 'html_instructions': 'Turn <b>left</b> onto <b>Av. Entre Ríos</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'fagvChufnKSAQlGQtGOfGARQtG'}, 'start_location': {'lat': -24.7811632, 'lng': -65.4115655}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.7 km', 'value': 704}, 'duration': {'text': '2 mins', 'value': 110}, 'end_location': {'lat': -24.7743912, 'lng': -65.41649629999999}, 'html_instructions': 'Turn <b>right</b> onto <b>Dr. A. Güemes</b>', 'maneuver': 'turn-right', 'polyline': {'points': 'j~fvC|wgnKwFSA?wBG_@CeBM{F_@_CE}BK{FY'}, 'start_location': {'lat': -24.7806986, 'lng': -65.4171075}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '1.3 km', 'value': 1256}, 'duration': {'text': '3 mins', 'value': 161}, 'end_location': {'lat': -24.7736054, 'lng': -65.42890799999999}, 'html_instructions': 'Turn <b>left</b> onto <b>12 de Octubre</b>', 'maneuver': 'turn-left', 'polyline': {'points': '|vevCbtgnKCpBI|CQnGI`CGlCIjCIhCK|F?PMnCEnCStGSrGGfCEhC'}, 'start_location': {'lat': -24.7743912, 'lng': -65.41649629999999}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '94 m', 'value': 94}, 'duration': {'text': '1 min', 'value': 17}, 'end_location': {'lat': -24.7744445, 'lng': -65.4290176}, 'html_instructions': 'Turn <b>left</b> onto <b>Pedernera</b><div style="font-size:0.9em">Destination will be on the left</div>', 'maneuver': 'turn-left', 'polyline': {'points': '`revCtajnKzBPh@B'}, 'start_location': {'lat': -24.7736054, 'lng': -65.42890799999999}, 'travel_mode': 'DRIVING'}], 'traffic_speed_entry': [], 'via_waypoint': []}, {'distance': {'text': '1.0 km', 'value': 1046}, 'duration': {'text': '3 mins', 'value': 158}, 'end_address': 'Aniceto Latorre 2515, Salta, Argentina', 'end_location': {'lat': -24.7721819, 'lng': -65.4332895}, 'start_address': 'Pedernera 1128, Salta, Argentina', 'start_location': {'lat': -24.7744445, 'lng': -65.4290176}, 'steps': [{'distance': {'text': '47 m', 'value': 47}, 'duration': {'text': '1 min', 'value': 7}, 'end_location': {'lat': -24.7748655, 'lng': -65.4290547}, 'html_instructions': "Head <b>south</b> on <b>Pedernera</b> toward <b>O' Higgins</b>", 'polyline': {'points': 'fwevCjbjnKtAD'}, 'start_location': {'lat': -24.7744445, 'lng': -65.4290176}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.1 km', 'value': 137}, 'duration': {'text': '1 min', 'value': 24}, 'end_location': {'lat': -24.7749679, 'lng': -65.4277067}, 'html_instructions': "Turn <b>left</b> at the 1st cross street onto <b>O' Higgins</b>", 'maneuver': 'turn-left', 'polyline': {'points': '|yevCpbjnKFeDJeB'}, 'start_location': {'lat': -24.7748655, 'lng': -65.4290547}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.1 km', 'value': 144}, 'duration': {'text': '1 min', 'value': 19}, 'end_location': {'lat': -24.7736835, 'lng': -65.42754359999999}, 'html_instructions': 'Turn <b>left</b> at the 1st cross street onto <b>Junín</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'pzevCdzinK_CQaCO'}, 'start_location': {'lat': -24.7749679, 'lng': -65.4277067}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.6 km', 'value': 554}, 'duration': {'text': '1 min', 'value': 77}, 'end_location': {'lat': -24.773332, 'lng': -65.43301629999999}, 'html_instructions': 'Turn <b>left</b> onto <b>12 de Octubre</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'nrevCbyinKGfCEhCK~CEnBGnBC`AAx@IzBM|D'}, 'start_location': {'lat': -24.7736835, 'lng': -65.42754359999999}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '0.1 km', 'value': 125}, 'duration': {'text': '1 min', 'value': 19}, 'end_location': {'lat': -24.7722143, 'lng': -65.4329048}, 'html_instructions': 'Turn <b>right</b> onto <b>Dr. Luis Güemes</b>', 'maneuver': 'turn-right', 'polyline': {'points': 'hpevCj{jnKwAIg@C_BI'}, 'start_location': {'lat': -24.773332, 'lng': -65.43301629999999}, 'travel_mode': 'DRIVING'}, {'distance': {'text': '39 m', 'value': 39}, 'duration': {'text': '1 min', 'value': 12}, 'end_location': {'lat': -24.7721819, 'lng': -65.4332895}, 'html_instructions': 'Turn <b>left</b> onto <b>Aniceto Latorre</b>', 'maneuver': 'turn-left', 'polyline': {'points': 'hievCrzjnKElA'}, 'start_location': {'lat': -24.7722143, 'lng': -65.4329048}, 'travel_mode': 'DRIVING'}], 'traffic_speed_entry': [], 'via_waypoint': []}], 'overview_polyline': {'points': 'hievCbmenKoCMItBGrAChA}Fc@wFYcEUcEQ{ES}B?{BFmBNiBRqBd@qFjAeJtByFnAwBh@VtA{@cFa@}B~Bi@hFiAvCs@bMqCbGcAQsCKa@Jg@~@P~@RtLnClIjB~J`CvFpAARrGvAv@JlKj@rVhAtR~@nPz@nJh@]lGw@|OcOq@}Nq@u@~XQtGwFSyBGeCQ{F_@_CEyJe@MnG[pKQxGIhCK|FM`DEnCg@hPMpGdDTtADFeDJeB_CQaCOGfCQhHSzIWxH_CM_BIElA'}, 'summary': 'Deán Funes', 'warnings': [], 'waypoint_order': [2, 1, 0]}]
    print('results:',results)
    camino=[]
    for i, leg in enumerate(results[0]["legs"]):
        print("##################################")
        print("i:",i)
        print("leg:",leg)
        print("==================================")
        print("Stop:" + str(i),
            leg["start_address"], 
            leg["start_location"], 
            "==> ",
            leg["end_address"], 
            "distance: ",  
            leg["distance"]["value"], 
            "traveling Time: ",
            leg["duration"]["value"]
        )
        print("##################################")
        camino.append((float(leg["end_location"]['lat']),float(leg["end_location"]['lng'])))
    print('camino:',camino)
#    0-Abuelo,1-Alicia,2-koki,3-loma
    lista_puntos_float=[(-24.774446,-65.428997),(-24.786493,-65.408791),(-24.758196,-65.408256),(-24.772197,-65.433291)]
    indices=[]
    for punto in camino:
        resultado=closest_node(punto,lista_puntos_float)
        print('resultado:',resultado)
        indices.append(resultado)
    print('indices:',indices)
    camino_definitivo=[]
    i=0
    for item in indices:
        camino_definitivo.append((i+1,str(lista_puntos_float[item][0])+','+str(lista_puntos_float[item][1])))
        i+=1
    print('camino_definitivo:',camino_definitivo)
    return camino_definitivo
#resultado= distancia_mas_larga(False,False,False)
resultado= mejor_ruta(False,False,False)
print('resultado:',resultado)
