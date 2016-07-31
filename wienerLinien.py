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
        return process.extract(userinput, self.stationNames, limit=6, scorer=fuzz.partial_ratio)

    def askStation(self):
        while True:
            result = self.fuzzyStationName(input())
            print(result)

            number = int(input())
            pprint(result[number - 1][2])


def main():
    wl = WienerLinien("stationen/cache/current.json")

    # pprint(wl.stations["214461789"])
    # pprint(wl.nexttrains(4431))
    wl.askStation()


if __name__ == '__main__':
    main()
