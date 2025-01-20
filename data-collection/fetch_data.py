import requests
import time
import csv

# Setting up constants
URL = 'https://re.jrc.ec.europa.eu/api/seriescalc' # hourly PV power and Wind at 10m in a year
GET_LIMIT_PER_SECOND = 30 # max number of GET requests per seconds on the API

def fetch_pvgis_data(points):
    # fetch and write [time, PV power, wind speed] in a csv file
    nb_get = 0
    with open('data-collection/pv_wind_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['longitude', 'latitude', 'year', 'month', 'day', 'hour', 'PV_power', 'WS10m'])
        for point in points : 
            nb_get += 1
            if(nb_get >= GET_LIMIT_PER_SECOND):
                print('time to sleep')
                time.sleep(1)
                nb_get = 0

            pvgis_params = dict(
                lon = point[0],
                lat = point[1],
                raddatabase = 'PVGIS-SARAH3',
                startyear = 2022,
                endyear = 2022,
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
                writer.writerow([point[0], point[1], dat['time'][:4], dat['time'][4:6], dat['time'][6:8], dat['time'][9:11], dat['P'], dat['WS10m']])
    return 0


# coordonnées de Brest et Montpellier
points = [[-4.48333, 48.400002],[3.862038, 43.62505]]
fetch_pvgis_data(points)
