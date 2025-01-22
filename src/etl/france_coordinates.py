import re
_='''
Metropolitan France coordinates : 
- North  : (51° 04' 18″ N, 2° 31' 42″ E) Bray-Dunes, Nord 
- East   : (42° 16' 56″ N, 9° 33' 36″ E) plage de Fiorentine, San-Giuliano, Haute-Corse
- South  : (41° 19'     N, 9° 15'     E) écueil de Lavezzi, îles Lavezzi, Bonifacio, Corse-du-Sud
- West   : (48° 26' 45″ N, 5° 09' 04″ W) phare de Nividic, Ouessant, Finistère

All metropolitan France coordinates are located in a rectangle between 2 points : 
- NW : (51° 04' 18″ N, 5° 09' 04″ W)
- SE : (41° 19' 00″ N, 9° 33' 36″ E)
'''

# Setting constants
PRECISION_IN_NEGATIVE_POWER = 1 # step in coordinates to dimensionate total time required to get all requested data
                                # sidenotes : using a step of E-1 is roughly equivalent to a delta the size of Paris
NW_LONGITUDE = "51° 04' 18″ N"
NW_LATITUDE = "5° 09' 04″ W"
SE_LONGITUDE = "41° 19' 00″ N"
SE_LATITUDE = "9° 33' 36″ E"
COORDINATES = [NW_LONGITUDE, NW_LATITUDE, SE_LONGITUDE, SE_LATITUDE]

def coordinates_to_float(coordinates):
    # transform longitude/latitude from string list to float list 
    results = []
    for coordinate in coordinates:
        vals = re.sub("[°'″]", '', coordinate).split(' ')
        if vals[3] == 'N' or vals[3] == 'E':
            results.append(round(int(vals[0]) + int(vals[1])/60 + int(vals[2])/3600, 3))
        else :
            results.append(round(-1 * (int(vals[0]) + int(vals[1])/60 + int(vals[2])/3600), 3))
    return results


def stats(COORDINATES, PRECISION_IN_NEGATIVE_POWER):
    # print total nb of points and time required to gather requested data
    NW_long, NW_lat, SE_long, SE_lat = coordinates_to_float(COORDINATES)
    delta_long = round(NW_long - SE_long, PRECISION_IN_NEGATIVE_POWER)*10**PRECISION_IN_NEGATIVE_POWER
    delta_lat = round(SE_lat - NW_lat, PRECISION_IN_NEGATIVE_POWER)*10**PRECISION_IN_NEGATIVE_POWER
    total_points = delta_lat * delta_long
    print("With a precision of E-{0} the total number of points is {1}".format(PRECISION_IN_NEGATIVE_POWER, total_points))
    
    # we can run 30 GET per second : How many seconds to handle every points taken
    nb_sec = (total_points / 30)
    print("With 30 GET per second the total time needed is {0} seconds, or {1} minutes".format(nb_sec, nb_sec/60))


def all_coordinates(coordinates=COORDINATES, precision_in_negative_power=PRECISION_IN_NEGATIVE_POWER):
    # return a list of all coordinates from extreme points coordinates and precision
    NW_long, NW_lat, SE_long, SE_lat = coordinates_to_float(coordinates)
    delta_long = int(round(abs(NW_long - SE_long), precision_in_negative_power) * 10 ** precision_in_negative_power)
    delta_lat = int(round(abs(SE_lat - NW_lat), precision_in_negative_power) * 10 ** precision_in_negative_power)
    results = []
    for i in range(delta_long):
        for j in range(delta_lat):
            results.append([round(SE_long - i * 10**(-1*precision_in_negative_power), precision_in_negative_power), 
                            round(NW_lat - j * 10**(-1*precision_in_negative_power), precision_in_negative_power)])
    return results 

# stats(COORDINATES, PRECISION_IN_NEGATIVE_POWER)
# print(len(all_coordinates()))

# print(all_coordinates())
# print([[x,y] for [x,y] in all_coordinates() where x < 40.9 and y < -14.6])
# print(len([[x,y] for [x,y] in all_coordinates() if x <= 41.3 and y <= -5.2]))
# print(all_coordinates()[0], all_coordinates()[1], all_coordinates()[-1])