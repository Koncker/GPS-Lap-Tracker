#module app laps

from myPyGPX import *
from laps import *
import math
import matplotlib


print("Reading track from file MaratonaAveiro2019.gpx")

# new setup: read another track form another GPX file
gpx = GPXDocument("MaratonaAveiro2019.gpx")
track = gpx.getTrack()

print("\nTrack Total Distance =", "{:.1f}".format(track.totalDistance()),"m")

trackTime = track.totalTime()

print("Track Total Time =", Analyse.secondsToHoursMinSec(trackTime))
print("\nExtracting laps from the track")
print("\nPace of each lap:")


lapExtractor = LapExtractor(track).getAutoLapsByDistance()
zeroFillSize = round(math.log(len(lapExtractor),10))

for element in lapExtractor:
    timeDeltaStr = Analyse.paceDecimalMinutesToMinSec(element.averageSpeed(expressAs = "pace"))
    
    print(str(element.getLapNumber()).zfill(zeroFillSize), ' ', timeDeltaStr)


print("\nPlot the laps with numbers [2, 10, 21, 37, 42, 43]")
print("\nNeed to CLOSE THE GRAPH WINDOW manually")

listOfLaps = [2,10,21,37,42,43]
listOfLapPoints = []

for i in range(len(listOfLaps)):
    for element in lapExtractor:
        if element.getLapNumber() == listOfLaps[i]:
            variable1 = (element.produceSeries(arrangeAs = "distance series", dataKind = "pace"))
            listOfLapPoints.append(Analyse.filterSeries(variable1, nForAverage = 5))
            Plot.add(listOfLapPoints[i], circlePoints = False, labelToUse = element.getLapNumber())


Plot.show()

print("\n----- End of execution -----")
