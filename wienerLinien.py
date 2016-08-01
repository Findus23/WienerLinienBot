#!/usr/bin/env python3
import json
from pprint import pprint
import requests
from config import *

from fuzzywuzzy import process, fuzz


class WienerLinien:
    def setStationNames(self):

        for station in self.stations.values():
            self.stationNames[station["HALTESTELLEN_ID"]] = station["NAME"]

    def __init__(self, json_path):
        with open(json_path) as json_file:
            self.stations = json.load(json_file)
        self.stationNames = {}
        self.setStationNames()

    @staticmethod
    def api(rbl):
        parameters = {"rbl": rbl, "sender": wienerlinien_API_key}
        r = requests.get("https://www.wienerlinien.at/ogd_realtime/monitor", params=parameters)
        print(r.status_code)
        return r.json()

    def nexttrains(self, rbl):
        response = self.api(rbl)
        countdowns = []
        name = response["data"]["monitors"][0]["lines"][0]["name"]
        towards = response["data"]["monitors"][0]["lines"][0]["towards"]
        for departure in response["data"]["monitors"][0]["lines"][0]["departures"]["departure"]:
            countdowns.append(departure["departureTime"]["countdown"])
        return countdowns, name, towards

    def fuzzy_stationname(self, userinput):
        output = process.extract(userinput, self.stationNames, limit=6, scorer=fuzz.UQRatio)
        choice = []
        for i in range(len(output)):
            if i == 0:
                diff = 0
            else:
                diff = output[i][1] - output[i - 1][1]
            if output[i][1] >= 55:
                if diff >= -7:
                    choice.append(output[i])
                else:
                    break

        return choice

    def askStation(self):
        while True:
            result = self.fuzzy_stationname(input())
            print(result)

            number = int(input())
            pprint(result[number - 1][2])

    def getStationInfo(self, station_id):
        return self.stations[str(station_id)]

    def get_platforms(self, station_id):
        return self.stations[str(station_id)]["PLATFORMS"]


def main():
    wl = WienerLinien("stationen/cache/current.json")

    # pprint(wl.stations["214461789"])
    # pprint(wl.nexttrains(4431))
    station = wl.fuzzy_stationname("Rossauer Lände")
    pprint(station[0])
    for platform in wl.get_platforms(station[0][2]):
        pprint(wl.nexttrains(platform["RBL_NUMMER"]))


if __name__ == '__main__':
    main()
