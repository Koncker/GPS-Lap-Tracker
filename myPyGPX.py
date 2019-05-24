# module myPyGPX

""" Provides tools to process tracks and routes obtained from GPX files. """

from math import pi, cos, sin, sqrt  # to compute distances between points
# note: math import becomes redundant since all names are available also as
# pylab.pi, pylab.cos, pylab.sin, pylab.sqrt
import pylab

import GPXparser


class GPXDocument:
    """ Representation of a GPX document. """

    def __init__(self, gpxFileName):
        """ Initializes a GPXDocument object by reading data from a file.

        Requires:
          gpxFileName is a string that names a reachable GPX file;
          this file contains at most 1 track;
          this file contains at most 1 route.
        """
        self.fileName = gpxFileName        
        self.currentTrack = None
        self.currentRoute = None	
        self.currentWayPoints = []        
        # read the GPX file and populate the object's attributes
        GPXparser.buildGPXDocument(gpxFileName, self)

    def getFileName(self):
        """ Returns the name of the file associated with this GPXDocument """
        return self.fileName
			
    def getTrack(self):
        """ Returns self's Track (the object representation of a track) """
        return self.currentTrack

    def setTrack(self, track):
        """ Sets self's Track """
        self.currentTrack = track
			
    def getRoute(self):
        """ Returns self's Route (the object representation of a route) """        
        return self.currentRoute

    def setRoute(self, route):
        """ Sets self's Route """
        self.currentRoute = route
        			
    def getWayPoints(self):
        """ Returns self's WayPoints (object representation of the waypoints)"""        
        return self.currentWayPoints

    def setWayPoints(self, waypoints):
        """ Sets self's Waypoints """
        self.currentWayPoints = waypoints


class Time:
    """ Representation of a moment in time """

    def __init__(self, year, month, day, hour, minute, second):
        """ Initializes the parameters according to most comon usage in GPX.

        Example of original information from a GPX file:
          <time>2018-04-08T12:34:28.250Z</time>
        Requires:
          all parameters are int, except second which may be float;
          1 <= month <= 12;
          1 <= day <= 31;
          other calendar restrictions for day as a function of year and month;
          0 <= hour <= 23;
          0 <= minute <= 59;
          0 <= second <= 59.999
        Note: fractional time is represented in GPX files down to millisecond.
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def timeInterval(self, other):
        """ Computes the difference between self and another Time.

        The result is given in seconds.
        Requires: self and other are instances of Time.
        Ensures: a float which is the time elapsed between other and self.
        """
        # import datetime
        # https://docs.python.org/3/library/datetime.html
        from datetime import datetime, timedelta
        # initialize datetime.datetime objects with
        # year, month, day, hour, minute, second, microsecond
        selfDatetime = datetime(self.year, self.month, self.day,
          self.hour, self.minute, int(self.second),
          int((self.second - int(self.second)) * 1000000))
        otherDatetime = datetime(other.year, other.month, other.day,
          other.hour, other.minute, int(other.second),
          int((other.second - int(other.second)) * 1000000))
        # compute the difference as a datetime.timedelta object
        timeDifference = selfDatetime - otherDatetime
        return timeDifference.total_seconds()
        
    def __str__(self):
        if self.second - int(self.second) < 0.0000005:
            representSecond = str(int(self.second))
        else:
            representSecond = format(self.second, '.3f')
        return str(self.year) + "-" + str(self.month) + "-" + str(self.day) \
          + " " + str(self.hour) + ":" + str(self.minute) \
          + ":" + representSecond


class Point:
    """ Representation of a point with coordinates and elevation.

    Common base class for different types of points.
    Direct base class for
      track points (class TrackPoint)
      and route points (class RoutePoint);
    Base class for
      waypoints (class Waypoint) trough inheritance from class RoutePoint.
    At this basic level, only a coordinate pair (latitude, longitude) and
    an elevation need to be assigned.
    """
    
    def __init__(self, lat, lon, elevation):
        """ Initializes coordinate pair (latitude, longitude) and elevation.

        Latitude and longitude coordinates are expressed in decimal degrees.
        Elevation is expressed in meters.
        Requires:
          lat, lon and elevation are float;
          -90.0 <= lat <= 90.0
          -180.0 <= lon <= 180.0
        """
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
      
    def getLatitude(self):
        return self.lat

    def getLongitude(self):
        return self.lon

    def getElevation(self):
        return self.elevation
    
    def distance(self, other):
        """ Computes the distance between self and another Point.

        The distance is expressed in meter.
        URL source: https://en.wikipedia.org/wiki/Geographic_coordinate_system
        Requires: other is an instance of Point.
        Ensures: a float which is the distance between the points.
        """
        latMid = (self.lat + other.lat)/2  # decimal degrees
        latMid = 2 * pi * latMid / 360     # radians
        meterPerDegreeLat = 111132.92 - 559.82 * cos(2 * latMid) \
                               + 1.175 * cos(4 * latMid) \
                               - 0.0023 * cos(6 * latMid)
        meterPerDegreeLon = 111412.84 * cos(latMid) \
                               - 93.5 * cos(3 * latMid) \
                               + 0.118 * cos(5 * latMid)
        deltaLat = abs(other.lat - self.lat)
        deltaLon = abs(other.lon - self.lon)
        distance_meters = sqrt((deltaLat * meterPerDegreeLat)**2 +
                               (deltaLon * meterPerDegreeLon)**2)
        return distance_meters


class TrackPoint(Point):
    """ Representation of a GPX track point. """    

    def __init__(self, lat, lon, time, elevation):
        """ Initializes a TrackPoint with a rich set of features.

        Initializes the coordinate pair (latitude, longitude) and the
        elevation required by Point. These are read from a GPX file.
        Quite often elevation is missing in the file, in which case it
        should be treated as zero.
        Initializes another attribute also directly read from a GPX file:
          time (according to GPX standard).
        These rich atributes need not follow the GPX standard.
        Requires: time is an instance of Time.
        """
        # Further attributes (to be computed later) are declared but
        # not instantiated here:
        # -- accumulatedDistance (in meter):
        #    this is the distance measured along the track, from the first
        #    track point until the present track point (self);
        #    its value is zero for the first track point
        # -- accumulatedElevation (in meter):
        #    this is the total vertical ascent measured along the track, from
        #    the first track point until the present track point (self);
        #    only considers positive accumulation, i.e., increments in
        #    elevation; decrements are ignored;
        #    its value is zero for the first track point
        # -- speed (in m/s):
        #    this is the instantaneous speed at the present track point (self),
        #    computed with respect to the previous point in the track;
        #    hence, it measures how fast the track "moved" from the previous to
        #    the present track point;
        #    by convention, the speed of the first track point (which cannot
        #    be computed) is set equal to the speed of the second track point
        # These rich atributes need not follow the GPX standard.
        #
        # read from GPX file; elevation may be absent
        super().__init__(lat, lon, elevation)
        self.time = time                 # Time
        # computed later with dedicated methods
        self.accumulatedDistance = None  # float
        self.accumulatedElevation = None # float
        self.speed = None                # float

    def getTime(self):
        return self.time

    def setAccumulatedDistance(self, accDist):
        self.accumulatedDistance = accDist

    def getAccumulatedDistance(self):
        return self.accumulatedDistance
    
    def setAccumulatedElevation(self, accElev):
        self.accumulatedElevation = accElev

    def getAccumulatedElevation(self):
        return self.accumulatedElevation    

    def setSpeed(self, speed):
        self.speed = speed

    def getSpeed(self):
        return self.speed 


class RoutePoint(Point):
    """ Representation of a GPX route point. """    

    def __init__(self, lat, lon, elevation = None,
                 name = None, description = None):
        """ Initilizes a RoutePoint with a specific set of features.

        Initializes the coordinate pair (latitude, longitude) and elevation
        required by Point.
        Adds new attributes.
        Examples:
          name = "motorway A5 - rtept 27"
          description = "turn right"
        Requires: name and description are strings.
        """
        super().__init__(lat, lon, elevation)
        self.name = name
        self.description = description
        

class WayPoint(RoutePoint):
    """ Representation of a GPX waypoint. """

    # Inherits __init__ from RoutePoint.
    # A WayPoint is initialized as a (special) RoutePoint
    # Examples:
    #   name = "gas station BP nr. 17"
    #   description = "turn right, after this"


class ListPoints:
    """ Representation of a conceptual list of points.

    Direct base class for
      TrackSeg
      and Route.
    """

    def __init__(self):
        self.pointList = []  # will hold Point as TrackPoint or RoutePoint

    def addPoint(self, point):
        """ Adds a point to self's list of points.

        Requires: point is an instance of Point.
        """
        self.pointList.append(point)

    def getPointList(self):
        return self.pointList


class TrackSeg(ListPoints):
    """ Representation of a GPX track segment. """
    

class Route(ListPoints):
    """ Representation of a GPX route. """
    

class Track:
    """ Representation of a GPX track. """

    def __init__(self):
        self.trackSegList = []  # list will contain TrackSeg

    def addTrackSeg(self, trackSeg):
        """ Requires: trackSeg is an instance of TrackSeg. """
        self.trackSegList.append(trackSeg)

    def getStartTime(self):
        """ Returns the starting time of self, in the form of a Time object. """
        return self.trackSegList[0].getPointList()[0].getTime()

    def getFinishTime(self):
        """ Returns the finishing time of self, in the form of a Time object."""
        return self.trackSegList[-1].getPointList()[-1].getTime()

    def produceSeries(self, arrangeAs = "time series", dataKind = "pace"):
        """ Produces a series with data from self, to use in further processing.

        The series originates from the track points that constitute the track.
        Produces a list of (x,y) pairs suitable e.g for statistical
        processing or for displaying in a plot.       
        Produces data in one of 2 different arrangements, which are suitable
        respectively for 2 different kinds of plots:
          a time series, where the x axis represents elapsed time in seconds;
          a distance series, where the x axis represents accumulated distance
            in meters.
        Data itself can be of 3 different kinds:
          instant pace in min/km (calculated);
            this is decimal pace, e.g., 4min30sec/km is represented as 4.5
          speed in km/h (calculated);
          elevation in meters (extracted directly from GPX file).
        Requires:
          arrangeAs = "time series" or "distance series";
          dataKind = "pace" or "speed km/h" or "elevation".
        Ensures: a list of (x,y) pairs of float.
        Robustness measure: to avoid instability in case the data contains one
          or more points with speed = 0.0, or very close to 0.0, the pace is
          artificially limited to a maximum given by the constant MAXIMUM_PACE.
        """
        # maximum allowed pace (a kind of constant):
        MAXIMUM_PACE = 60.0
        # this implies that the minimum allowed speed is...
        MINIMUM_SPEED = 100 / (6 * MAXIMUM_PACE)
        # ensure that the data has been computed, before being accessed
        if arrangeAs == "distance series":
            self._computeAccDistanceForEachTrackPoint()
        if dataKind in ["pace", "speed km/h"]:
            self._computeSpeedForEachTrackPoint()
        # decide which getter to use for the X component
        if arrangeAs == "time series":
            initialTime = self.getStartTime()
            def _getX(trackPoint):
                return trackPoint.getTime().timeInterval(initialTime)
        else:  # arrangeAs == "distance series"
            def _getX(trackPoint):
                return trackPoint.getAccumulatedDistance()
        # decide which getter to use for the Y component
        if dataKind == "pace":
            def _getY(trackPoint):
                speed = trackPoint.getSpeed()
                # test to ensure that the speed is not too close to zero
                if speed > MINIMUM_SPEED:
                    pace = (1/speed) * 100/6
                else:
                    pace = MAXIMUM_PACE
                return pace
        elif dataKind == "speed km/h":
            def _getY(trackPoint):
                speed = trackPoint.getSpeed()
                speedKm_H = speed * 36/10
                return speedKm_H
        else:  # dataKind == "elevation"
            def _getY(trackPoint):
                return trackPoint.getElevation()
        # now iterate over the track points in the track            
        result = []
        for trackSegment in self.trackSegList:
            for trackPoint in trackSegment.getPointList():
                result.append((_getX(trackPoint), _getY(trackPoint)))
        return result 

    def produceXYdata(self):
        """ Produces a list of XY coordinates from self, for further processing.

        The list originates from the track points that constitute the track.
        Produces a list of (x,y) pairs suitable e.g for statistical
        processing or for displaying in a plot.       
        Produces data corresponding to an XY track, thus registering movement
        along the XY geographical plane.
        Note that:
          X corresponds to longitude;
          Y corresponds to latitude.
        Ensures: a list of (x,y) pairs of float.
        """
        result = []
        for trackSegment in self.trackSegList:
            for trackPoint in trackSegment.getPointList():
                result.append((trackPoint.getLongitude(),
                               trackPoint.getLatitude()))
        return result

    def _computeAccDistanceForEachTrackPoint(self):
        """ Computes the accumulatedDistance attribute of each track point.

        accumulatedDistance is expressed in meter.
        This is the distance measured along the track, from the first
        track point until each track point.
        Its value is zero for the first track point.
        Ensures (as a side-effect):
            the attribute is computed for all the track points of self. 
        """
        firstSegment = True
        for trackSegment in self.trackSegList:
            pointList = trackSegment.getPointList()
            if firstSegment:
                pointList[0].setAccumulatedDistance(0)
                firstSegment = False
            else: # firstSegment == False
                distanceFromPrevious = \
                    pointList[0].distance(lastPointPrevTrkSeg)
                newAccumulatedDistance = \
                    lastPointPrevTrkSeg.getAccumulatedDistance() + \
                    distanceFromPrevious
                pointList[0].setAccumulatedDistance(newAccumulatedDistance)
            for i in range(1, len(pointList)):
                distanceFromPrevious = pointList[i].distance(pointList[i-1])
                newAccumulatedDistance = \
                    pointList[i-1].getAccumulatedDistance() + \
                    distanceFromPrevious
                pointList[i].setAccumulatedDistance(newAccumulatedDistance)
            lastPointPrevTrkSeg = pointList[-1]

    def _computeAccElevationForEachTrackPoint(self):
        """ Computes the accumulatedElevation attribute of each track point.

        accumulatedElevation is expressed in meter.
        This is the total vertical ascent measured along the track, from
        the first track point until each track point.
        Only considers positive accumulation, i.e., increments in
        elevation. Decrements are ignored.
        Its value is zero for the first track point.
        Ensures (as a side-effect):
            the attribute is computed for all the track points of self. 
        """
        firstSegment = True
        for trackSegment in self.trackSegList:
            pointList = trackSegment.getPointList()
            if firstSegment:
                pointList[0].setAccumulatedElevation(0)
                firstSegment = False
            else: # firstSegment == False
                verticalDistanceFromPrevious = pointList[0].getElevation() - \
                    lastPointPrevTrkSeg.getElevation()
                if verticalDistanceFromPrevious < 0:
                    verticalDistanceFromPrevious = 0
                newAccumulatedElevation = \
                    lastPointPrevTrkSeg.getAccumulatedElevation() + \
                        verticalDistanceFromPrevious
                pointList[0].setAccumulatedElevation(newAccumulatedElevation)
            for i in range(1, len(pointList)):
                verticalDistanceFromPrevious = pointList[i].getElevation() - \
                    pointList[i-1].getElevation()
                if verticalDistanceFromPrevious < 0:
                    verticalDistanceFromPrevious = 0
                newAccumulatedElevation = \
                    pointList[i-1].getAccumulatedElevation() + \
                    verticalDistanceFromPrevious
                pointList[i].setAccumulatedElevation(newAccumulatedElevation)
            lastPointPrevTrkSeg = pointList[-1]

    def _computeSpeedForEachTrackPoint(self):
        """ Computes the speed attribute of each track point.

        speed is expressed in m/s.
        This is the instantaneous speed at each track point,
        computed with respect to the previous point in the track.
        Hence, it measures how fast the track "moved" from the previous to
        the present track point, for each track point.
        By convention, the speed of the first track point (which cannot
        be computed) is set equal to the speed of the second track point.
        Ensures (as a side-effect):
            the attribute is computed for all the track points of self. 
        """
        firstSegment = True
        for trackSegment in self.trackSegList:
            pointList = trackSegment.getPointList()
            if firstSegment:
                pointList[0].setSpeed(None)  # to be assigned at the end
                firstSegment = False
            else: # firstSegment == False
                distanceFromPrevious = \
                    pointList[0].distance(lastPointPrevTrkSeg)
                timeLapseFromPrevious = pointList[0].getTime().timeInterval(
                    lastPointPrevTrkSeg.getTime())               
                pointList[0].setSpeed(
                    distanceFromPrevious/timeLapseFromPrevious)
            for i in range(1, len(pointList)):
                distanceFromPrevious = pointList[i].distance(pointList[i-1])
                timeLapseFromPrevious = pointList[i].getTime().timeInterval(
                    pointList[i-1].getTime())
                pointList[i].setSpeed(
                    distanceFromPrevious/timeLapseFromPrevious)
            lastPointPrevTrkSeg = pointList[-1]
        # go back and initialize the speed of the 1st track point as equal
        # to the speed of the second track point
        # assuming 1st track segment contains at least 2 track points
        firstPointList = self.trackSegList[0].getPointList()
        firstPointList[0].setSpeed(firstPointList[1].getSpeed())

    def getSerialized(self):
        """ Returns the track points of self in a simple list.

        The points appear in the list in the same order as in the track,
        but they are not wrapped in a TrackSeg or a Track object.
        The accumulatedDistance attribute is initialized before the list is
        returned.
        Ensures:
          a list containing the track points of self;
          each track point has its accumulatedDistance attribute initialized.
        """
        # ensure accumulatedDistance attribute is initialized
        self._computeAccDistanceForEachTrackPoint()
        # iterate over the trackSegs in the track, to build the resulting list          
        result = []
        for trackSegment in self.trackSegList:
            result.extend(trackSegment.getPointList())
        return result

    def hidePartOfTrack(self, center_lat, center_lon, radius):
        """ Returns a new Track object resulting from deleting points from self.

        The points that are deleted are all those whithin a circle of radius
        radius from a center point with latitude and longitude given by
        center_lat and center_lon respectively.
        Radius is measured in meters.
        The aim is to hide tracks in sensitive areas such as home location,
        forbidden areas, etc.
        Does not keep any track segment which ends up with less than
          2 track points.
        """
        # developer's note: the minimum size of 2 for track segments should be
        # enforced in the contracts (pre-conditions) of other methods
        centerPoint = Point(center_lat, center_lon, 0) # elevation is irrelevant
        newTrack = Track()
        for trackSegment in self.trackSegList:
            newTrackSegment = TrackSeg()
            for trackPoint in trackSegment.getPointList():
                if trackPoint.distance(centerPoint) > radius:
                    newTrackSegment.addPoint(trackPoint)
            if len(newTrackSegment.getPointList()) > 1:
                newTrack.addTrackSeg(newTrackSegment)
        return newTrack        

    def totalTime(self):
        """ Returns the total time of this track.

        This is the elapsed time between the first and the last points of the
        track.
        Time is in seconds.
        Related: see method Analyse.secondsToHoursMinSec()
        """
        return self.getFinishTime().timeInterval(self.getStartTime())

    def totalDistance(self):
        """ Returns the total accumulated distance of this track. """
        lastPoint = self.trackSegList[-1].getPointList()[-1]
        result = lastPoint.getAccumulatedDistance()
        if result == None:  # attribute has not been set
            self._computeAccDistanceForEachTrackPoint()
            result = lastPoint.getAccumulatedDistance()
        return result

    def totalAccumulatedElevation(self):
        """ Returns the total accumulated positive elevation of this track.

        Only considers the positive contributions in elevation differences.
        """
        lastPoint = self.trackSegList[-1].getPointList()[-1]
        result = lastPoint.getAccumulatedElevation()
        if result == None:  # attribute has not been set
            self._computeAccElevationForEachTrackPoint()
            result = lastPoint.getAccumulatedElevation()
        return result

    def averageSpeed(self, expressAs = "pace"):
        """ Returns the average speed of this track.

        This is the average speed of someone passing through each of the
        track points at a time given by the respective timestamp.
        Speed is expressed as:
          expressAs = "pace" or "speed km/h"
        Pace means min/km. It is decimal pace.
        Related: see method Analyse.paceDecimalMinutesToMinSec()
        """
        averageSpeedMetersPerSecond = self.totalDistance()/self.totalTime()
        if expressAs == "pace":
            result = (1/averageSpeedMetersPerSecond) * 100/6
        else:  # expressAs = "speed km/h"
            result = averageSpeedMetersPerSecond * 36/10
        return result

# ----------------------------------------   
# Further processing, analysis, statistics
# ----------------------------------------
    
class Analyse:
    """ Provides methods for GPX data processing. """

    @staticmethod
    def filterSeries(series, nForAverage = 1):
        """ Smooths a series (e.g., a time series) with a "low-pass" filter.
        
        A "low-pass" filter is implemented as a running average over the
        last nForAverage data points.
        The parameter nForAverage denotes the number of data points
        (present + previous) used in the running average.
        If nForAverage is chosen as 1, no filtering is done (only the present
        data point is used).
        Requires:
          series is a list of (x,y) pairs of float;
          nForAverage is an int;
          nForAverage >= 1;
          len(series) >= nForAverage.
        Ensures:
          a new list of (x,y) pairs of float with the same size as series;
          each x in an output (x,y) pair is unaltered when compared to the
          respective input (x,y);
          each y in an output (x,y) pair is the average of the last nForAverage
          values of y.
        """
        result = []
        # first phase: smoothing the first nForAverage - 1 points
        for i in range(nForAverage - 1):
            newYvalue = \
              sum([series[j][1] for j in range(i+1)]) / (i+1)
            result.append((series[i][0], newYvalue))
        # second phase: smoothing the remaining points
        for i in range(nForAverage - 1, len(series)):
            newYvalue = \
              sum([series[j][1] for j in range(i-nForAverage+1, i+1)]) / \
                nForAverage
            result.append((series[i][0], newYvalue))
        return result

    @staticmethod
    def secondsToHoursMinSec(timeInSeconds):
        """ Converts time in seconds to the hour:minute:second format.

        Requires: timeInSeconds is a non-negative float.
        Ensures: a string in the format hh:mm:ss where
          mm is between 00 and 59;
          ss is between 00 and 59, implying rounding to the unit digit;
          hh starts in 0 but is not limited to 24 or 99; it can be e.g. 396.
        """
        timeInSeconds = round(timeInSeconds) # int
        hours = timeInSeconds // 3600
        minutes = (timeInSeconds % 3600) // 60
        seconds = timeInSeconds % 60
        hours = str(hours)
        minutes = str(minutes)
        if len(minutes) == 1:
            minutes = "0"+minutes
        seconds = str(seconds)
        if len(seconds) == 1:
            seconds = "0"+seconds
        return hours+":"+minutes+":"+seconds
         
    @staticmethod
    def paceDecimalMinutesToMinSec(paceInDecimalMinutes):
        """ Converts decimal pace to the (minute:second)/km format.

        Example: 4.5 (min/km) converts to the string "4:30/km"
        Requires: paceInDecimalMinutes is a non-negative float.
        Ensures: a string in the format mm:ss/km where
          ss is between 00 and 59, implying rounding to the unit digit;
          mm starts in 0 but is not limited to 60 or 99; it can be e.g. 472.
        """
        minutes = int(paceInDecimalMinutes)
        decimalPart = paceInDecimalMinutes - minutes
        seconds = decimalPart * 60
        seconds = round(seconds)  # int
        if seconds == 60:
            seconds = 0
            minutes += 1
        minutes = str(minutes)
        seconds = str(seconds)
        if len(seconds) == 1:
            seconds = "0"+seconds
        return minutes+":"+seconds+"/km"


# --------
# Plotting
# --------

# A simple wrapper for PyLab, which itself is a wrapper for matplotlib etc.
# Provides only basic functionality to make plots as required for this project.
# Future work: add further functionality: captions, titles, etc.

class Plot:
    """ Provides methods for showing data in plots. """

    @staticmethod
    def add(listOfPairs, circlePoints = False, labelToUse = ""):
        """ Adds a list of pairs to the current (eventually composite) plot.

        Only one current composite plot is supported at any given time.
        After this plot is shown, and the respective window is destroyed,
        another plot may be started.
        Each addition of a set of points to the current plot is done by a call
        to add (the method defined here).
        If circlePoints == True, circles are drawn around individual points.
        An optional label labelToUse can be associated with the set of points.
        """
        if circlePoints:
            style = '-o'
        else:
            style = '-'
        # although the following line calls the method plot(), it actually
        # produces only a part of a (composite) plot
        pylab.plot([pair[0] for pair in listOfPairs],
                   [pair[1] for pair in listOfPairs],
                   style, label = labelToUse)
        pylab.legend()

    @staticmethod
    def show():
        """ Shows the current plot as a window in the desktop.

        Note: in the Windows operating system, the window must be killed for
        program execution to proceed.
        """
        pylab.show()


