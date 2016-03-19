import requests
import os
import json

class DirGet(object):
    '''Get directions between two SF Locations'''

    def __init__(self):
        self.start = 'https://maps.googleapis.com/maps/api/directions/json?'
        self.key = os.environ['AMBLER_API']

    def get_dirs(self, origin, end, waypoints=None):
        origin = ''.join(origin.split())
        end = ''.join(end.split())
        params ='origin=' + origin + '&destination=' + end
        params += '&mode=walking'
        if waypoints:
            params.join([point + '|' for point in waypoints])
        params += '&key=' + self.key
        return requests.get(self.start + params)


if __name__ == '__main__':
    getter = DirGet()
    response = getter.get_dirs('466ClementinaSt', 'FortPointOverlook')
    with open('samp_jsons.txt', 'w') as f:
        json.dump(response.json(), f)
