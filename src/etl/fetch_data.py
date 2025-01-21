import requests
import time
import csv
import os
import france_coordinates as fr_coor

# Setting up constants
URL = 'https://re.jrc.ec.europa.eu/api/seriescalc' # hourly PV power and Wind at 10m in a year
RADDATABASE = 'PVGIS-SARAH3'
STARTYEAR = 2022
ENDYEAR = 2022
GET_LIMIT_PER_SECOND = 30 # max number of GET requests per seconds on the API
LIMIT_LINES_PER_FILE = 2000000
DATA_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+'/data/raw/'
METADATA_FILE = 'metadata.txt'

def get_last_state():
    if os.path.exists(METADATA_FILE):
        with open(DATA_PATH + METADATA_FILE, 'r') as f:
            last_state = f.readline().strip().split(',')
            file_number = int(last_state[0])
            last_longitude = int(last_state[1])
            last_latitude = int(last_state[2])
            line_count = int(last_state[3])
    else :
        file_number = 0
        last_longitude = 1000
        last_latitude = 1000
        line_count = 0
    return file_number, last_longitude, last_latitude, line_count

def save_state(file_number, longitude, latitude, line_count):
    with open(DATA_PATH + METADATA_FILE, 'w') as f:
        f.write(f"{file_number},{longitude},{latitude},{line_count}\n")

def fetch_pvgis_data(points):
    # fetch and write [time, PV power, wind speed] in a csv file
    total_points = len(points)
    get_count = 0
    point_count = 0

    file_number, last_longitude, last_latitude, line_count = get_last_state()
    current_file_name = DATA_PATH+'pv_wind_data_{}.csv'.format(file_number)

    # with a metadata file counting the number of files and the lines where we left off, we can reassemble the iterator position in points[{value}:]

    with open(current_file_name, 'a') as current_file:
        for point in [[x,y] for [x,y] in points if x <= last_longitude]: # targeting the right longitude is done, need to handle latitude positioning
            if line_count == 0:
                line = 'longitude,latitude,year,month,day,hour,PV_power,WS10m'
                current_file.write(line)
                line_count = 1
            elif line_count >= LIMIT_LINES_PER_FILE:
                file_number += 1
                current_file_name = DATA_PATH+'pv_wind_data_{}.csv'.format(file_number)
                with open(current_file_name, 'w') as current_file:
                    line = 'longitude,latitude,year,month,day,hour,PV_power,WS10m'
                    current_file.write(line)
                    line_count = 1

            if(get_count >= GET_LIMIT_PER_SECOND):
                time.sleep(1)
                get_count = 0
                print("{0} / {1} ({2}%)".format(point_count, total_points, round(100*point_count/total_points)))

            pvgis_params = dict(
                lon = point[0],
                lat = point[1],
                raddatabase = RADDATABASE,
                startyear = STARTYEAR,
                endyear = ENDYEAR,
                pvcalculation = 1,
                peakpower = 1,
                loss = 0,
                outputformat = 'json'
            )

            params = "&".join([f'{key}={value}' for key, value in pvgis_params.items()])
            response = requests.get(URL, params=params)
            data = response.json()
            try:
                data['outputs']
            except KeyError:
                # the json response is allegedly a string indicating that the point is located in the sea
                continue
            for dat in data['outputs']['hourly']:
                line = "{},{},{},{},{},{},{},{}\n".format(point[0], point[1], dat['time'][:4], dat['time'][4:6], dat['time'][6:8], dat['time'][9:11], dat['P'], dat['WS10m'])
                current_file.write(line)
                line_count += 1
                save_state(file_number, point[0], point[1], line_count)
            get_count += 1
            point_count += 1
            
    return 0


# coordonnées de Brest et Montpellier
_='''points = [[-4.48333, 48.400002],[3.862038, 43.62505],[-4.48333, 48.400002]]
fetch_pvgis_data(points)'''

fr_points = fr_coor.all_coordinates()
fetch_pvgis_data(fr_points)