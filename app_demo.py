import requests
import os
import json
import pandas as pd
import numpy as np
import itertools
import webbrowser

class DirGet(object):
    '''Run essentially the whole project in this one class'''

    def __init__(self):
        '''1. Start with a list of possible waypoints to hit (curate this)
        2. Score those waypoints based on a few different filter criteria
        3. Select the filters that apply to you and return waypoints that meet those criteria
        4. Find all the routes through those waypoints
        5. Pick the routes that end up closest to the distance that you want
        6. Print a bunch of good information about the route and the waypoints
        7. Figure out someway to communicate this to a design team and display some html
        8. Learn swift'''
        self.start = 'https://maps.googleapis.com/maps/api/directions/json?'
        self.key = os.environ['MAPS_API']

    def get_dirs(self, origin, end, waypoints=None):
        '''Get directions between two locations via several waypoints'''
        origin = ''.join(origin.split())
        end = ''.join(end.split())
        params ='origin=' + origin + '&destination=' + end
        params += '&mode=walking'
        params += '&waypoints=optimize:true|' + ''.join(['via:'+ point + '|' for point in waypoints])
        params += '&key=' + self.key
        return requests.get(self.start + params)

    def get_top_points(self, waypoints, filters):
        '''Return the waypoints from our curated list that meet the filters you selected
        the more points you get, the higher you get on the list'''
        scores = []
        for row in waypoints.iterrows():
            row = row[1]
            score = 0
            for col in row.index:
                if col in filters:
                    score += row[col]
            scores.append(score)
        indices = np.argsort(scores)[::-1]
        points = waypoints[indices]['address']
        return np.array(points)

    def get_all_routes(self, origin, points, end=None, min_points=2, max_points=10):
        '''Get all the routes between the origin, the endpoint while hitting all the waypoints inbetween
        Limit the number of places to visit by min and max points
        Visit many different combinations of waypoints'''
        if not end:
            end = origin  # you can't actually do this and still have other things work
        response_list = []
        points_ = []
        # Save lists of routes and the waypoints you hit
        for i in xrange(min_points, max_points):
            for point_ in itertools.combinations(points, i):
                point_ = np.array(point_)
                points_.append(point_)
                response_list.append(self.get_dirs(origin, end, point_))
        return np.array(response_list), np.array(points_)

    def check_routes(self, distance, response_list, points):
        '''Sort the routes and waypoint list by routes that are closest to your requested distance'''
        distance = 1609.34 * distance  # distance in meters
        distances = []
        for response in response_list:
            if len(response.json()['routes']):
                route = response.json()['routes'][0]
                summary = route['legs'][0]
                distances.append(summary['distance']['value'])
        distances = np.abs(np.array(distances) - distance)
        indices = np.argsort(distances)
        return response_list[indices], points[indices]

    def return_info(self, response, points, waypoints):
        '''Print this out
        This is where the info would communicate with design if we knew how to do that'''
        summary = response.json()['routes'][0]['legs'][0]
        print 'Distance: ', summary['distance']['text']
        print 'Time: ', summary['duration']['text']
        mask = waypoints['address'].apply(lambda x: x in points)
        print 'Points Visited:'
        for row in waypoints[mask].iterrows():
            print row.name
            webbrowser.open(row['picture url'])

if __name__ == '__main__':
    getter = DirGet()
    # Sample of our curated content
    df = pd.read_csv('sample_waypoints.csv')
    waypoints = df[0:8].copy()
    filters = ['beauty', 'art', 'vista']
    # These are the points that most algin with our filters
    points = getter.get_top_points(waypoints, filters)
    # These are the routes and associated waypoint combinations
    response_list, points = getter.get_all_routes('466ClementinaSt', points, end='FortPointOverlook', max_points=3)
    # These are the routes and associated waypoint combinations sorted by how closely they match the distance you want
    routes, points = getter.check_routes(6, response_list, points)
    # Print it out
    for i in xrange(5):
        getter.return_info(routes[i], points[i], waypoints)

    # Sample Output:
    # Distance:  5.8 mi
    # Time:  1 hour 58 mins
    # Points Visited:
    # Ocean Beach
    # Mission Dolores
    # (Image opens in your browser)
    #

    # with open('sample_json.txt', 'wa') as f:
    #         json.dump([route.json() for route in routes], f)
