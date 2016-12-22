import requests as r
import json

apiKey = "AIzaSyDKL9iF-TujlZqANx3DSEkD-EpQ5XW5DNs"
resp = r.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=Kings+County,+NY&destinations=Los+Angeles+County,+CA&key=%s" % apiKey)
print(json.loads(resp.text)["rows"][0]["elements"][0]["distance"]["value"])
