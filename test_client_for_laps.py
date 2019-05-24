from laps import *

print("\n----- Testing some methods from module laps -----")


print("\nfile FR935-25_04_2018_dois_trksegs_com_waypoints.gpx")

# setup: read a  track from a GPX file
gpx = GPXDocument("FR935-25_04_2018_dois_trksegs_com_waypoints.gpx")
track = gpx.getTrack()

print("\nTesting Lap.__init__() by creating a lap with the entire track:")
testLap = Lap(1, 0, track.getSerialized())
print("Total lap distance =", testLap.totalDistance())
print("Total distance of reference track =", track.totalDistance())

print("\nTesting Lap.getLapNumber():")
print(testLap.getLapNumber())

print("\nTesting Lap.getStartingDistance():")
print(testLap.getStartingDistance())

print("\nTesting Lap.getFastestPace():")
print(testLap.getFastestPace(7))
print(testLap.getFastestPace(7, measureAlong = "time"))

print("\nTesting Lap.getSlowestPace():")
print(testLap.getSlowestPace(7))
print(testLap.getSlowestPace(7, measureAlong = "time"))

print("\nTesting LapExtractor.getLapsFromListOfTimeMarkers():")

lapExtractor = LapExtractor(track)

listOfLapsFromTimeMarkers = \
  lapExtractor.getLapsFromListOfTimeMarkers([3600, 7200])

totalDistanceSumLaps = 0
print("lap number | lap distance | lap time | lap starts at distance")
for lap in listOfLapsFromTimeMarkers:
    print(lap.getLapNumber(), " ", lap.totalDistance(), " ", lap.totalTime(),
          " ", lap.getStartingDistance())
    totalDistanceSumLaps += lap.totalDistance()
print("\nsum of all laps distances =", totalDistanceSumLaps)

print("track total distance =", track.totalDistance())


print("\nfile MaratonaAveiro2019.gpx")

# new setup: read another track form another GPX file
gpx = GPXDocument("MaratonaAveiro2019.gpx")
track = gpx.getTrack()

print("\nTesting LapExtractor.getLapsFromListOfTimeMarkers():")

lapExtractor = LapExtractor(track)

listOfLapsFromTimeMarkers = \
  lapExtractor.getLapsFromListOfTimeMarkers([3600, 7200, 10800])

totalDistanceSumLaps = 0
print("lap number | lap distance | lap time | lap starts at distance")
for lap in listOfLapsFromTimeMarkers:
    print(lap.getLapNumber(), " ", lap.totalDistance(), " ", lap.totalTime(),
          " ", lap.getStartingDistance())
    totalDistanceSumLaps += lap.totalDistance()
print("\nsum of all laps distances =", totalDistanceSumLaps)

print("track total distance =", track.totalDistance())


print("\n----- End of tests -----")


