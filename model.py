# model.py

import data
import turtle as t
import pickle
import math as m
import csv
import us
import requests as r
import json

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
    print(distx, disty)
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

for i in abbs:
    start = i[0]
    end = i[1]
    startcoords = [coordsf[start][1], coordsf[start][2]]
    endcoords = [coordsf[end][1], coordsf[end][2]]
    startname = coordsf[start][0].replace(" ", "+")
    endname = coordsf[end][0].replace(" ", "+")
    resp = r.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s" % (
    startname, endname, apiKey))
    dist = json.loads(resp.text)["rows"][0]["elements"][0]["distance"]["value"]
    coordsff.append([startname, endname, dist])
    t.up()
    t.setpos(startcoords[0], startcoords[1])
    t.down()
    t.setpos(endcoords[0], endcoords[1])
    t.up()
    
for i in coordsff:
    print(i)

t.exitonclick()