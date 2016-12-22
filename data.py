# data.py

import requests as r
import json
import geocoder as g
import time
import pickle

queryPause = 0.09
# Pause after iteration to stay below Google's query limit
apiKey = "6ca66ba6d62443a3ccc9d04e7e3c1c3796162652"
# Census Bureau API Key
nullStates = [2, 3, 7, 14, 15, 43, 52]
# nullStates is either states that are exclaves or FIPS codes that do not exist

def fetchStates():
	print("Fetching states...")
	result = []
	for i in range(1, 57):
		if i not in nullStates:
			d = r.get("http://api.census.gov/data/2015/acs1?get=NAME,B01001_001E&for=state:%s&key=%s" % (i, apiKey))
			data = json.loads(d.text)
			# Calls the U.S. Census Bureau API to get a full list of states and their FIPS codes, puts them in JSON format
			# dataf = json.dumps(data, sort_keys=True, indent=2)
			result.append(data[1])
	return result

def fetchPopCities():
	states = fetchStates()
	print("Fetching populations...")
	final = []
	for state in states:
		fips = int(state[2])
		d = r.get("http://api.census.gov/data/2013/acs3?get=NAME,B01001_001E&for=county:*&in=state:%i&key=%s" % (fips, apiKey))
		data = json.loads(d.text)
		max = 0
		for i in data:
			try:
				if int(i[1]) > max:
					max = int(i[1])
			except ValueError:
				continue
		maxPop = ""
		for i in data:
			try:
				if int(i[1]) == max:
					maxPop = i
					break
			except ValueError:
				continue
		final.append(maxPop)
	return final

def fetchLatLong(data):
	params = data[0]
	out = g.google(params)
	time.sleep(queryPause)
	sw = out.json["bbox"]["southwest"]
	ne = out.json["bbox"]["northeast"]
	latlong = [data[0], (sw[0] + ne[0]) / 2, (sw[1] + ne[1]) / 2]
	# Finds the midpoint of the southeast/northwest bounds of the given county/city
	return latlong


def constructArray():
	cityData = fetchPopCities()
	print("Fetching coordinates...")
	finalPops = []
	for i in cityData:
		finalPops.append(fetchLatLong(i))
	pickle.dump(finalPops, open("city_data.p", "wb"))
	return finalPops