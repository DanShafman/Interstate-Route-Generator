# model.py

import data
import turtle as t
import pickle
import math as m
import csv
import us
import requests as r
import json
import pprint as p

try:
    final = pickle.load(open("city_data.p", "rb"))
except:
    data.constructArray()
    final = pickle.load(open("city_data.p", "rb"))
# Loads the array of cities and coordinates from data.py

count = 0
baseCircum = 24874/360
# The length of one degree longitude at the equator

t.speed(10)
t.ht()
coords = []
print("Drawing...")
for i in final:
    disty = (i[1] * baseCircum / 3.5) - 750
    # distx = (float(i[2] * m.cos(m.radians(i[1])) * baseCircum) / 3.5) + 1400
    # Cosine function of lat. gets long. and compensates for the earth's curved surface
    distx = (i[2] * baseCircum / 3.5) + 1900
    print(count, i[0])
    t.penup()
    t.setpos(distx, disty)
    t.pendown()
    # t.circle(10)
    t.write(count)
    count += 1
    coords.append([i[0], distx, disty])

#========================CUTOFF=====================

def loadAbbs():
    # Loads the state abbreviations from a CSV file
    z = []
    with open('neighbors-states.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')
        for row in spamreader:
            x = str(row[0][0] + row[0][1] + row[0][2] + row[0][3] + row[0][4]).split(",")
            if "AK" not in x and "HI" not in x:
                z.append(x)
    return z
abbs = loadAbbs()

coordsf = {}
# coordsf becomes a dictionary, with the key being a state abbreviation and the value being
# the corresponding value in coords
for i in range(0, len(coords)):
    name = (coords[i][0].split(", "))[1]
    abbr = ""
    for j in us.states.STATES:
        if name == j.name:
            abbr = j.abbr
            break
    coordsf[abbr] = coords[i]

apiKey = "AIzaSyDKL9iF-TujlZqANx3DSEkD-EpQ5XW5DNs"
# For Google Distance Matrix API

coordsff = []

def drawModel():
    count = 0
    for i in abbs:
        start = i[0]
        end = i[1]
        startcoords = [coordsf[start][1], coordsf[start][2]]
        endcoords = [coordsf[end][1], coordsf[end][2]]
        startname = coordsf[start][0].replace(" ", "+")
        endname = coordsf[end][0].replace(" ", "+")
        # try:
        #     resp = r.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s" % (
        #     startname, endname, apiKey))
        #     dist = json.loads(resp.text)["rows"][0]["elements"][0]["distance"]["value"]
        #     coordsff.append([[startname, startcoords], [endname, endcoords], dist])
        # except:
        #     print(count, "Using pickle data...")
        #     count += 1
        #     coordsff.append([[startname, startcoords], [endname, endcoords]])
        print(count, "Using pickle data...")
        count += 1
        coordsff.append([[startname, startcoords], [endname, endcoords]])
        t.up()
        t.setpos(startcoords[0], startcoords[1])
        t.down()
        t.setpos(endcoords[0], endcoords[1])
        t.up()
        # pickle.dump(coordsff, open("final_array.p", "wb"))

for i in coordsff:
    print(i, "\n")

def drawComplete():
    coordsff = pickle.load(open("final_array.p", "rb"))
    p.pprint(coordsff)
    print(findNeighbors([115.44533077936512, -112.13783629047612], coordsff))
    startq = input("Enter start location: ")
    endq = input("Enter end location: ")
    startpos = ""; endpos = ""
    alg = input("Select [D]ijkstra's or [A]* algorithm: ")
    for i in coordsff:
        for j in range(0, 2):
            if i[j][0] == startq:
                startpos = i[j][1]
            elif i[j][0] == endq:
                endpos = i[j][1]
            elif startpos != "" and endpos != "":
                break
        if startpos != "" and endpos != "":
            break
    if alg.upper() == 'D':
        dijkstra(startpos, endpos, coordsff)
    elif alg.upper() == 'A':
        astar(startpos, endpos, coordsff)
    else:
        print("Enter A or D.")
        drawComplete()

# Algorithm functions begin here

def dijkstra(startpos, endpos, coords_passed):
    numIts = 0
    distances = [[0, startpos, []]]
    visited = []
    t.color("red")
    t.width(4)
    t.up()
    t.setpos(startpos[0], startpos[1])
    currCounty = startpos
    # Sets the current county to the designated start
    while currCounty != endpos:
        visited.append(currCounty)
        # Adds the current county to the visited set
        for i in findNeighbors(currCounty, coords_passed):
            # Only cycles through unvisited neighbors
            numIts += 1
            if i not in visited:
                distToNeighbor = getDistFromList(currCounty, distances) + findDist(currCounty, i, coords_passed)
                # Distance to neighbor is the dist of the current county + distance to neighbor
                if getDistFromList(i, distances) != None:
                    # If the city neighbor county already has a distance asigned to it...
                    neighborCurrentDist = getDistFromList(i, distances)
                    # ...assign the smaller of the two distances
                    if distToNeighbor < neighborCurrentDist:
                        x = getPathFromList(currCounty, distances)
                        x.append(currCounty)

                        distances.remove([neighborCurrentDist, i, getPathFromList(i, distances)])
                        distances.append([distToNeighbor, i, x])
                else:
                    x = getPathFromList(currCounty, distances)
                    x.append(currCounty)
                    distances.append([distToNeighbor, i, x])

        distances.sort()

        for i in distances:
            # Sets the current location to the lowest unvisited distance
            if i[1] not in visited:
                t.setpos(i[1][0], i[1][1])
                break
        currCounty = list(t.pos())

    path = getPathFromList(endpos, distances)
    path.append(endpos)
    for i in path:
        # Draws the path from start to end in red
        t.setpos(i[0], i[1])
        t.down()
    print("numIts:", numIts)
    print("path:", getPathFromList(endpos, distances))
    print("distance:", getDistFromList(endpos, distances))

def astar(startpos, endpos, coords_passed):
    # Nearly identical to dijkstra's, with the exception of the heuristicCostEstimate
    # variable
    numIts = 0
    distances = [[0, startpos, []]]
    visited = []
    t.color("red")
    t.width(4)
    t.up()
    t.setpos(startpos[0], startpos[1])
    currCounty = startpos
    # Sets the current county to the designated start
    while currCounty != endpos:
        visited.append(currCounty)
        # Adds the current county to the visited set
        for i in findNeighbors(currCounty, coords_passed):
            # Only cycles through unvisited neighbors
            numIts+=1
            if i not in visited:
                distToNeighbor = getDistFromList(currCounty, distances) + findDist(currCounty, i, coords_passed)
                # Distance to neighbor is the dist of the current county + distance to neighbor

                heuristicCostEstimate = (getStraightLineDist(i, endpos, coords_passed) * baseCircum / 3.5) + 1900
                # Sets the heuristic cost estimate to the length of the
                # straight line connecting the neighbor and the final
                # point
                if getPathFromList(i, distances) != None:
                    # If the city neighbor county already has a distance asigned to it...
                    neighborCurrentDist = getDistFromList(i, distances)
                    # ...assign the smaller of the two distances
                    if (distToNeighbor + heuristicCostEstimate) < neighborCurrentDist:
                        x = getPathFromList(currCounty, distances)
                        x.append(currCounty)

                        distances.remove([neighborCurrentDist, i, getPathFromList(i, distances)])
                        distances.append([distToNeighbor + heuristicCostEstimate, i, x])
                else:
                    x = getPathFromList(currCounty, distances)
                    x.append(currCounty)
                    distances.append([distToNeighbor + heuristicCostEstimate, i, x])

        distances.sort()

        for i in distances:
            # Sets the current location to the lowest unvisited distance
            if i[1] not in visited:
                t.setpos(i[1][0], i[1][1])
                break
        currCounty = list(t.pos())

    path = getPathFromList(endpos, distances)
    path.append(endpos)
    for i in path:
        # Draws the path from start to end in red
        t.setpos(i[0], i[1])
        t.down()
    print("numIts:", numIts)
    print("path:", getPathFromList(endpos, distances))
    # print("distance:", getDistFromList(endpos, distances))

def findNeighbors(city, coords_passed):
    # Returns the neighbors of the selected county
    neighbors = []
    for i in coords_passed:
        if i[0][1] == city:
            neighbors.append(i[1][1])
        elif i[1][1] == city:
            neighbors.append(i[0][1])
    return neighbors

def findDist(city1, city2, coords_passed):
    # Returns the distance from one county to another adjacent one
    for i in coords_passed:
        # print(city1, i[0][1])
        # p.pprint(coordsff)
        if i[0][1] == city1 or i[1][1] == city1:
            if i[0][1] == city2 or i[1][1] == city2:
                return i[2]

def getDistFromList(city, distList):
    for i in distList:
        if i[1] == city:
            return i[0]

def getPathFromList(city, distList):
    for i in distList:
        if i[1] == city:
            y = i[2][:]
            return y

def getStraightLineDist(city1, city2, coords_passed):
    # Formula for distance between two points
    xVal = (city1[0] - city2[0]) ** 2
    yVal = (city1[1] - city2[1]) ** 2
    return (xVal + yVal) ** 0.5

drawModel()
drawComplete()

t.exitonclick()
