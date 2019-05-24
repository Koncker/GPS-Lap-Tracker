# module laps

from copy import deepcopy

from myPyGPX import *

class Lap(Track):
    """ A lap during an activity; extracted from some track of that activity.

    Lap created during an activity of running, cycling, swimming, etc.
    Typically, each new lap is started automatically at fixed distance or time
    intervals; but laps may also be started "manually" during the activity,
    using distance or time markers that may result in non-uniform distance
    or time intervals.
    """

    def __init__(self, lapNumber, startingDistance, listOfPoints):
        """ Creates a lap, from a list of track points.

        Since each lap is created by some creational object or process, each new
        lap should be viewed as the next lap in a sequence of laps extracted
        from some track.
        Requires:
          a positive int lapNumber;
          a non-negative number startingDistance, which represents the distance
          from the start of the track as measured in the beginning of the lap;
          a list of sequential track points (i.e., objects of class TrackPoint).
        """
        super().__init__()
        self.lapNumber = lapNumber
        self.startingDistance = startingDistance
        trackSegment = TrackSeg()

        for element in listOfPoints:
            trackSegment.addPoint(element)


        self.trackSegList.append(trackSegment)


    def getTrackSegList(self):
        """ Returns a list of points.
        """
        return self.trackSegList
        
    def getLapNumber(self):
        """ Returns the lap number.
        
        This lap number is the position of this lap in the sequence of laps
        extracted from some reference track.
        """
        return self.lapNumber

    def getStartingDistance(self):
        """ Returns the accumulated distance at the beginning of the lap.

        The accumulated distance is measured from the start of the reference
        track.
        """
        return self.startingDistance

    # could be a method from super-class Track!
    def getFastestPace(self, nForAverage, measureAlong = "distance"):
        """ Returns the pair (location of fastest pace, fastest pace).

        Pace is instant pace at each track point and is expressed in min/km.
        Thus, a smaller pace is a faster pace.
        If measureAlong = "distance", the location is given as accumulated
        distance from the beginning of the lap.
        If measureAlong = "time", the location is given as elapsed time since
        the beginning of the lap.
        To avoid the effects of noise in the series of track points, the series
        is filtered using nForAverage points.
        nForAverage = 1 means no averaging is done.
        See the static method Analyse.filterSeries().
        Requires:
          nForAverage is an int;
          nForAverage >= 1;
          nForAverage <= the number of track points in this lap;
          measureAlong = "distance" or "time".
        Ensures:
          a pair of non-negative numbers with, respectively, the location
          of the fastest pace along the lap, and the fastest pace itself;
          if the fastest pace is found at different locations, only the last
          location is returned.
        """
        seriesList = Track.produceSeries(self, measureAlong +" series")
        seriesList = Analyse.filterSeries(seriesList, nForAverage)

        maxPace = None

        for element in seriesList:
                if (maxPace == None):
                    maxPace = element
                elif(element[1] < maxPace[1]):
                    maxPace = element

        return maxPace

    # could be a method from super-class Track!
    def getSlowestPace(self, nForAverage, measureAlong = "distance"):
        """ Returns the pair (location of slowest pace, slowest pace).

        Pace is instant pace at each track point and is expressed in min/km.
        Thus, a larger pace is a slower pace.
        If measureAlong = "distance", the location is given as accumulated
        distance from the beginning of the lap.
        If measureAlong = "time", the location is given as elapsed time since
        the beginning of the lap.
        To avoid the effects of noise in the series of track points, the series
        is filtered using nForAverage points.
        nForAverage = 1 means no averaging is done.
        See the static method Analyse.filterSeries().
        Requires:
          nForAverage is an int;
          nForAverage >= 1;
          nForAverage <= the number of track points in this lap;
          measureAlong = "distance" or "time".
        Ensures:
          a pair of non-negative numbers with, respectively, the location
          of the slowest pace along the lap, and the slowest pace itself;
          if the slowest pace is found at different locations, only the last
          location is returned.
        """

        seriesList = Track.produceSeries(self, measureAlong +" series")
        seriesList = Analyse.filterSeries(seriesList, nForAverage)

        minPace = None

        for element in seriesList:
                if (minPace == None):
                    minPace = element
                elif(element[1] > minPace[1]):
                    minPace = element

        return minPace


class LapExtractor:
    """ Provides methods to extract and build laps from some track. """
    
    def __init__(self, referenceTrack):
        """ At creation time, connects self with its reference track.

        More specifically, initializes as attribute the list of all
        track points from the reference track.
        """
        # obtain a simple list of TrackPoint from the reference track:
        self.serializedTrack = referenceTrack.getSerialized()

    def getSerializedTrack(self):
        return self.serializedTrack

    # auxiliary method
    def _split(self, listOfSplitIndices):
        """ Returns a list of laps from the reference track.

        Each int value contained in listOfSplitIndices is an index of the list
        self.serializedTrack.
        The laps are created taking the given indices as boundaries.
        Each index (an int value contained in listOfSplitIndices) corresponds
        to the beginning of a new lap in the corresponding position in
        self.serializedTrack:
        -- index 0 of listOfSplitIndices contains index 0 of
        self.serializedTrack and denotes the beginning of the 1st lap;
        -- index 1 of listOfSplitIndices contains some int > 0 and denotes the
        beginning of the 2nd lap in some position of self.serializedTrack;
        -- etc.
        Each index (except 0) of listOfSplitIndices also indicates the end of
        the previous lap in the corresponding position in self.serializedTrack:
        -- index 1 of listOfSplitIndices contains some int > 0 and denotes the
        end of the 1st lap in the corresponding position in
        self.serializedTrack;
        -- etc.
        Requires:
          listOfSplitIndices[0] = 0;
          listOfSplitIndices[i+1] > listOfSplitIndices[i],
          thus ensuring that no lap will have less than 2 track points;
          listOfSplitIndices[-1] = len(self.serializedTrack) - 1.
        Ensures:
          a list of consecutive laps where each lap has at least 2 track points.
        """
        listOfLaps = []
        lapNumber = 0
        for i in range(len(listOfSplitIndices)-1):
            lapNumber += 1
            # obtain the list of track points for the next lap to be created;
            # the track points are cloned form a section of the (serialized)
            # reference track
            nextListOfPoints = \
              deepcopy(self.serializedTrack[listOfSplitIndices[i]:
                                            listOfSplitIndices[i+1] + 1])
            # register the initialAccumulatedDistance of this lap, with respect
            # to the beginning of the track
            initialAccumulatedDistance = \
                                nextListOfPoints[0].getAccumulatedDistance()
            # reset the accumulated distance within the lap, taking as internal
            # reference the first point of the lap
            for point in nextListOfPoints:
                point.setAccumulatedDistance( \
                  point.getAccumulatedDistance() - initialAccumulatedDistance)
            # now create the lap with its corresponding list of track points
            nextLap = Lap(lapNumber,
                          initialAccumulatedDistance,
                          nextListOfPoints)
            # apend the newly created lap to the list of laps
            listOfLaps.append(nextLap)
        return listOfLaps

    def getAutoLapsByDistance(self, autoSplitValue = 998.03):
        """ Obtains the list of laps from the serialized track. 

        The laps are split based on accumulated distance, at constant intervals
        with length autoSplitValue.
        Requires: autoSplitValue is a positive number representing meters.
        Ensures: a list of consecutive laps where the last point of a lap is
          also the first point of the next lap.
        """
        # build the list of split indices
        listOfSplitIndices = [0]
        index = 1
        while index < len(self.serializedTrack):
            # define a distance as measured along the lap, starting from 0
            # at the first point of the lap
            lapDistance = 0
            initialAccumulatedDistance = \
                        self.serializedTrack[index - 1].getAccumulatedDistance()
            while lapDistance < autoSplitValue and \
                  index < len(self.serializedTrack):            
                lapDistance = \
                  self.serializedTrack[index].getAccumulatedDistance() - \
                  initialAccumulatedDistance
                index += 1
            # if either lapDistance >= autoSplitValue
            #        or index = len(self.serializedTrack)
            # then the end of a lap has been reached;
            # the end of the lap is registered at index - 1 to compensate
            # for the increment index += 1 at the end of the loop body
            listOfSplitIndices.append(index - 1)
        # pass the list of split indices to the auxiliary method _split()
        # to obtain a list of laps from the reference track
        return self._split(listOfSplitIndices)

    def getAutoLapsByTime(self, autoSplitValue = 240.0):
        """ Obtains the list of laps from the serialized track. 

        The laps are split based on elapsed time, at constant intervals with
        length autoSplitValue.
        Requires: autoSplitValue is a positive number representing seconds.
        Ensures: a list of consecutive laps where the last point of a lap is
          also the first point of the next lap.
        """
        # build the list of split indices
        listOfSplitIndices = [0]
        index = 1
        while index < len(self.serializedTrack):
            # define elapsed time as measured along the lap, starting from 0
            # at the first point of the lap
            lapTime = 0
            initialTime = self.serializedTrack[index - 1].getTime()
            while lapTime < autoSplitValue and \
                  index < len(self.serializedTrack):            
                lapTime = \
                 self.serializedTrack[index].getTime().timeInterval(initialTime)
                index += 1
            # if either lapTime >= autoSplitValue
            #        or index = len(self.serializedTrack)
            # then the end of a lap has been reached;
            # the end of the lap is registered at index - 1 to compensate
            # for the increment index += 1 at the end of the loop body
            listOfSplitIndices.append(index - 1)
        # pass the list of split indices to the auxiliary method _split()
        # to obtain a list of laps from the reference track
        return self._split(listOfSplitIndices)

    def getLapsFromListOfDistanceMarkers(self, listOfMarkers):
        """ Obtains the list of laps from the serialized track. 

        The laps are split based on accumulated distance as measured from
        the start of the reference track, not from the begining of each lap.
        The split points are read from listOfMarkers.
        Requires:
          listOfMarkers is a list of non-negative numbers in
          increasing order, representing accumulated distance in meters;
          the last value of listOfMarkers must be >= the total distance of the
          reference track.
        Ensures:
          a list of consecutive laps where the last point of a lap is also
          the first point of the next lap.
        """
        # build the list of split indices
        listOfSplitIndices = [0]
        index = 1        # index refers to the list self.serializedTrack
        markerIndex = 0  # markerIndex refers to the list listOfMarkers
        while index < len(self.serializedTrack):
            # read the next split point from the list of markers
            nextSplitPoint = listOfMarkers[markerIndex]
            # use total accumulated distance from the begining of the reference
            # track, not from the begining of the lap
            totalAccDistance = \
              self.serializedTrack[index - 1].getAccumulatedDistance()
            while totalAccDistance < nextSplitPoint and \
                  index < len(self.serializedTrack):            
                totalAccDistance = \
                  self.serializedTrack[index].getAccumulatedDistance()
                index += 1
            listOfSplitIndices.append(index - 1)
            markerIndex += 1
        # pass the list of split indices to the auxiliary method _split()
        # to obtain a list of laps from the reference track
        return self._split(listOfSplitIndices)
    
    def getLapsFromListOfTimeMarkers(self, listOfMarkers):
        """ Obtains the list of laps from the serialized track. 

        The laps are split based on elapsed time as measured from the start
        of the reference track, not from the begining of each lap.
        The split points are read from listOfMarkers.
        Requires:
          listOfMarkers is a list of non-negative numbers in increasing order,
          representing elapsed time in seconds;
          the last value of listOfMarkers must be >= the total time of the
          reference track.
        Ensures:
          a list of consecutive laps where the last point of a lap is also
          the first point of the next lap.
        """

        # build the list of split indices
        listOfSplitIndices = [0]
        index = 1        # index refers to the list self.serializedTrack
        markerIndex = 0  # markerIndex refers to the list listOfMarkers
        startTime = self.serializedTrack[0].getTime()
        while index < len(self.serializedTrack):
            # read the next split point from the list of markers
            nextSplitPoint = listOfMarkers[markerIndex]
            # use total accumulated distance from the begining of the reference
            # track, not from the begining of the lap
            totalAccTime = self.serializedTrack[index - 1].getTime().timeInterval(startTime)
            while totalAccTime < nextSplitPoint and index < len(self.serializedTrack):            
                totalAccTime = self.serializedTrack[index].getTime().timeInterval(startTime)
                index += 1
            listOfSplitIndices.append(index - 1)
            markerIndex += 1
        # pass the list of split indices to the auxiliary method _split()
        # to obtain a list of laps from the reference track
        return self._split(listOfSplitIndices)
