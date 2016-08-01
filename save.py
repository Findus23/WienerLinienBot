#!/usr/bin/env python3
import yaml
from pprint import pprint


class PersistentData:
    def __init__(self):
        with open("save.yaml") as json_file:
            self.save = yaml.load(json_file)

    def export(self):
        with open('save.yaml', 'w') as outfile:
            outfile.write(yaml.dump(self.save, default_flow_style=False))

    def user(self, chat_id, firstname, lastname):
        if chat_id not in self.save:
            self.save[chat_id] = {}
        if "stations" not in self.save[chat_id] or self.save[chat_id]["stations"] is None:
            self.save[chat_id]["stations"] = []
        self.save[chat_id]["name"] = firstname + " " + lastname

    def save_choice(self, chat_id, choice):
        self.save[chat_id]["choice"] = choice

    def get_choice(self, chat_id):
        return self.save[chat_id]["choice"]

    def add_station(self, chat_id, station):
        pprint(self.save[chat_id])
        self.save[chat_id]["stations"].append(station)
        self.delete_choice(chat_id)

    def delete_choice(self, chat_id):
        del self.save[chat_id]["choice"]

    def get_stations(self, chat_id):
        return self.save[chat_id]["stations"]
