import math
from math import radians, cos, sin, asin, sqrt
from decimal import *

class GeoHelper():
    message = ''
    earthRadius = 6371.0 # kilometer
    initialDistance = 10 #km, initial distance to use for nearby search
    maxDistance = 200 #km, max distance for nearby search
    maxIteration = 5 #max number of iteration to get nearby items
    targetCount = 25 #target number of nearby items to get
    targetMargin = 5 #+ and - this number of items from the target number to stop
    
    #get the revised distance to search based on the current result count
    def reviseDistance(self, currentDistance, currentCount):
        if currentCount <= 0:
            return self.maxDistance
        newDistance = float(currentDistance) * math.sqrt(self.targetCount) / math.sqrt(currentCount)
        if newDistance > self.maxDistance:
            return self.maxDistance
        return newDistance
    
    #get the square with certain distance (kilometer) from the center point (with lat, lon)
    #return a range object with latMin, latMax, lonMin, lonMax
    def getSquare(self, center, distance):
        center['latR'] = float(center['lat']) * math.pi/180
        center['lonR'] = float(center['lon']) * math.pi/180
        radius = float(distance) / self.earthRadius
        
        range = {}
        point = {}
        point = self.getDestinationR(center, radius, 0)
        range['latMax'] = point['lat']
        point = self.getDestinationR(center, radius, 90)
        range['lonMax'] = point['lon']
        point = self.getDestinationR(center, radius, 180)
        range['latMin'] = point['lat']
        point = self.getDestinationR(center, radius, 270)
        range['lonMin'] = point['lon']
        return range
    
    #get the destination point from the start point (with lat, lon), distance away, in the bearing direction
    #return the end point object (with lat, lon)
    def getDestination(self, startPoint, distance, bearing):
        radius = float(distance) / self.earthRadius
        self.getDestinationR(self, startPoint, radius, bearing)
        
    #get the destination point from the start point, certain earth radius away, in the bearing direction
    #return the end point object (with lat, lon)
    def getDestinationR(self, startPoint, radius, bearing):
        R = self.earthRadius
        lat1 = float(startPoint['lat']) * math.pi/180
        lon1 = float(startPoint['lon']) * math.pi/180
        bearingR = float(bearing) * math.pi/180
        
        lat2 = math.asin( math.sin(lat1)*math.cos(radius) + 
                math.cos(lat1)*math.sin(radius)*math.cos(bearingR) )
        lon2 = lon1 + math.atan2(math.sin(bearingR)*math.sin(radius)*math.cos(lat1), 
                math.cos(radius)-math.sin(lat1)*math.sin(lat2))
        endPoint = {}
        endPoint['lat'] = lat2 * 180/math.pi
        endPoint['lon'] = lon2 * 180/math.pi
        return endPoint;

    def toRadius(self, i):
        return float(i) * math.pi / 180

    def toDegree(self, i):
        return Decimal(str(float(i) * 180 / math.pi))
    
    def getDistance(self, startPoint, endPoint):
        """
        Calculate the great circle distance in miles between two points 
        on the earth (specified in decimal degrees)
        """
        lon1, lat1, lon2, lat2 = float(startPoint['lon']), float(startPoint['lat']), float(endPoint['lon']), float(endPoint['lat'])
        
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        #km = 6367 * c
        miles = 3956.26916 * c
        return miles
    