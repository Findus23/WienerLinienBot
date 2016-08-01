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
        return r.json()

    def nexttrains(self, rbl):
        response = self.api(rbl)
        countdowns = []
        for departure in response["data"]["monitors"][0]["lines"][0]["departures"]["departure"]:
            countdowns.append(departure["departureTime"]["countdown"])
        return countdowns

    def fuzzy_stationname(self, userinput):
        output = process.extract(userinput, self.stationNames, limit=6, scorer=fuzz.partial_ratio)
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

    def getStationInfo(self, stationId):
        return self.stations[str(stationId)]


def main():
    wl = WienerLinien("stationen/cache/current.json")

    # pprint(wl.stations["214461789"])
    # pprint(wl.nexttrains(4431))
    pprint(wl.fuzzy_stationname("Heiligenstadt"))


if __name__ == '__main__':
    main()
