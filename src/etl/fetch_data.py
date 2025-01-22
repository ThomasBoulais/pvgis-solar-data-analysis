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
LIMIT_LINES_PER_FILE = 1000000
DATA_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+'/data/raw/'
METADATA_FILE = 'metadata.txt'

def get_last_state():
    if os.path.exists(DATA_PATH + METADATA_FILE):
        with open(DATA_PATH + METADATA_FILE, 'r') as f:
            last_state = f.readline().strip().split(',')
            file_number = int(last_state[0])
            last_longitude = float(last_state[1])
            last_latitude = float(last_state[2])
            line_count = int(last_state[3])
    else :
        file_number = 0
        last_longitude = 1000
        last_latitude = None
        line_count = 0
    return file_number, last_longitude, last_latitude, line_count

def save_state(file_number, longitude, latitude, line_count):
    with open(DATA_PATH + METADATA_FILE, 'w') as f:
        f.write(f"{file_number},{longitude},{latitude},{line_count}\n")

def get_remaining_points(points, last_longitude, last_latitude):
    if last_latitude is None:
        last_latitude = points[0][1]
    nb_lat_to_skip = int(round((last_latitude - points[0][1]) / (points[1][1] - points[0][1]))) + 1
    remaining_points = [[x,y] for [x,y] in points if x <= last_longitude][nb_lat_to_skip:]
    return remaining_points

def get_params(longitude, latitude):
    pvgis_params = dict(
        lon = longitude,
        lat = latitude,
        raddatabase = RADDATABASE,
        startyear = STARTYEAR,
        endyear = ENDYEAR,
        pvcalculation = 1,
        peakpower = 1,
        loss = 0,
        outputformat = 'json'
        )
    params = "&".join([f'{key}={value}' for key, value in pvgis_params.items()])
    return params

def fetch_pvgis_data(points):
    # fetch and write [time, PV power, wind speed] in csv files
    total_points = len(points)
    get_count = 0
    point_count = 0
    
    file_number, last_longitude, last_latitude, line_count = get_last_state()
    current_file_name = DATA_PATH+'pv_wind_data_{}.csv'.format(file_number)
    remaining_points = get_remaining_points(points, last_longitude, last_latitude)

    with open(current_file_name, 'a') as current_file:
        for point in remaining_points:
            if not (0 < line_count < LIMIT_LINES_PER_FILE):
                if line_count >= LIMIT_LINES_PER_FILE:
                    file_number += 1
                    current_file_name = DATA_PATH+'pv_wind_data_{}.csv'.format(file_number)
                    current_file.close()
                    current_file = open(current_file_name, 'w')
                line = 'longitude,latitude,year,month,day,hour,PV_power,WS10m\n'
                current_file.write(line)
                line_count = 1

            if(get_count >= GET_LIMIT_PER_SECOND):
                # intended as request per second limiter, but used as a progression marker because the threshold seems unobtainable
                # time.sleep(1)
                get_count = 0
                print("{0} / {1} ({2}%)".format(point_count, total_points, round(100*point_count/total_points)))

            params = get_params(point[0], point[1])
            response = requests.get(URL, params=params)
            data = response.json()
            try:
                data['outputs']
            except KeyError:
                # json response is a string indicating the point is located in the sea and doesn't yield any relevant value
                continue
            for dat in data['outputs']['hourly']:
                line = "{},{},{},{},{},{},{},{}\n".format(point[0], point[1], dat['time'][:4], dat['time'][4:6], dat['time'][6:8], dat['time'][9:11], dat['P'], dat['WS10m'])
                current_file.write(line)
                line_count += 1
                save_state(file_number, point[0], point[1], line_count)
            get_count += 1
            point_count += 1
    current_file.close()        
    return 0


_='''points = [
    [2.3, 48.8],[2.3, 48.7], [2.3, 48.6],
    [2.2, 48.8],[2.2, 48.7]
            ]'''

_='''points = [
    [2.3, 48.8],[2.3, 48.7], [2.3, 48.6],
    [2.2, 48.8],[2.2, 48.7], [2.2, 48.6],
    [2.1, 48.8],[2.1, 48.7], [2.1, 48.6]
            ]'''

fr_points = fr_coor.all_coordinates()
fetch_pvgis_data(fr_points)
