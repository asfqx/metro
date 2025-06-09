import random
import mesa
import mesa_geo as mg
from shapely.geometry import Point
from .models import Train, Station, Passenger
import random


class MetroModel(mesa.Model):
    def __init__(self, data):
        super().__init__()
        self.grid = mg.GeoSpace()
        self.steps = 0
        self.lines = {}
        self.passengers = {}
        self.trains = {}
        self.stations = {}
        self.next_id = 0
        self.build_network(data)
        self.deploy_trains(data)
        self.deploy_passengers(data)

    def build_network(self, data):
        for line_id, line in data["Lines"].items():
            stations = line["stations"]
            self.lines[line_id]["name"] = line["name"]
            coords = [(x, y) for x, y in random.sample(range(1, 20), 2)]
            for station in stations:
                x = random.sample(coords, 1)[0]
                y = random.sample(coords, 1)[1]
                st = Station(station, self, Point(x, y), line["name"])
                self.stations[station] = st
                self.lines[line_id]["stations"].append(st)

        # Connect stations within lines
        for line in self.lines.values():
            stations = line["stations"]
            for i in range(len(stations) - 1):
                stations[i].add_connection(stations[i + 1], line["name"])
                stations[i + 1].add_connection(stations[i], line["name"])

        # Add all stations to grid
        all_stations = []
        for line in self.lines.values():
            all_stations.extend(line["stations"])
        self.grid.add_agents(all_stations)

    def deploy_trains(self, data):
        """Deploy trains on different lines with varied routes"""
        for line_id, line in data["Lines"].items():
            trains = line["trains"]

            for train in trains:
                tr = Train(
                    train,
                    self,
                    self.lines[line_id]["stations"][0].geometry,
                    data["Trains"][train]["route"],
                    line["name"],
                    speed=random.random(),
                )
                self.grid.add_agents(tr)
                self.trains[train] = tr

    def deploy_passengers(self, data):
        for passenger_id, passenger in data["Passengers"].items():
            ps = Passenger(
                passenger_id,
                self.stations[passenger["start_st_id"]],
                self.stations[passenger["end_st_id"]],
                model=self,
            )
            self.grid.add_agents(ps)
            self.passengers[passenger_id] = ps

    def update(self, data):
        for passenger_id, passenger in data["Passengers"].items():
            if passenger_id not in self.passengers.keys():
                ps = Passenger(
                    passenger_id,
                    self.stations[passenger["start_st_id"]],
                    self.stations[passenger["end_st_id"]],
                    model=self,
                )
                self.grid.add_agents(ps)
                self.passengers[passenger_id] = ps
            if (
                self.passengers[passenger_id].current_station.unique_id
                != passenger["current_station"]
            ):
                self.passengers[passenger_id].current_station = self.stations[
                    passenger["current_station"]
                ]
            if (
                self.passengers[passenger_id].current_train.unique_id
                != passenger["current_train"]
            ):
                self.passengers[passenger_id].current_train = self.trains[
                    passenger["current_train"]
                ]
        for train_id, train in data["Trains"].items():
            if train_id not in self.trains.keys():
                tr = Train(
                    train_id,
                    self,
                    self.lines[train["line"]]["stations"][0].geometry,
                    data["Trains"][train]["route"],
                    train["line"],
                    speed=random.random(),
                )
                self.grid.add_agents(tr)
                self.trains[train_id] = tr
        self.step()

    def step(self):
        self.steps += 1
        for agent in self.grid.agents:
            if isinstance(agent, Train) or isinstance(agent, Passenger):
                agent.move()
