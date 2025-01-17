import requests
import pandas as pd

# daily average value in a given month
URL = 'https://re.jrc.ec.europa.eu/api/DRcalc'
# hourly value
URL = 'https://re.jrc.ec.europa.eu/api/seriescalc'


def fetch_pvgis_data(lat, lon):
    
    pvgis_params = dict(
        lat = lat,
        lon = lon,
        raddatabase = 'PVGIS-SARAH3',
        pvcalculation = 1,
        peakpower = 1,
        loss = 0,
        outputformat = 'json'
    )

    params = "&".join([f'{key}={value}' for key, value in pvgis_params.items()])

    print(params)
    response = requests.get(URL, params=params)
    data = response.json()
    for dat in data['outputs']['hourly']:
        year = dat['time'][:4]
        month = dat['time'][4:6]
        day = dat['time'][6:8]
        hour = dat['time'][9:11]
        min = dat['time'][11:13]
        print("time : ", year, "", month, "", day, "", hour, "", min, "", "Power : ", dat['P'], "\tWind speed at 10m : ", dat['WS10m'])
    _='''month = data['outputs']['daily_profile']
    for hour in month:
        print(hour)'''
    return 0


# coordonnées de Montpellier
# fetch_pvgis_data(43.62505, 3.862038)

# coordonnées de Brest
fetch_pvgis_data(48.400002, -4.48333)