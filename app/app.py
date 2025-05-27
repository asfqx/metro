import random
import mesa
import mesa_geo as mg
from shapely.geometry import Point
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from collections import defaultdict


class Station(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, line_colors=None):
        super().__init__(model=model, geometry=geometry, crs="epsg:3857")
        self.unique_id = unique_id
        self.line_colors = line_colors if line_colors else ["#000000"]
        self.waiting_passengers = []
        self.connections = defaultdict(list)  # {line_name: [connected_stations]}

    def add_passenger(self, passenger):
        self.waiting_passengers.append(passenger)

    def remove_passenger(self, passenger):
        if passenger in self.waiting_passengers:
            self.waiting_passengers.remove(passenger)

    def add_connection(self, station, line_name):
        if station not in self.connections[line_name]:
            self.connections[line_name].append(station)


class Train(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, route, line_name, speed=0.05):
        super().__init__(model=model, geometry=geometry, crs="epsg:3857")
        self.unique_id = unique_id
        self.route = route
        self.line_name = line_name
        self.current_station_idx = 0
        self.direction = 1  # 1 forward, -1 backward
        self.passengers = []
        self.capacity = 30
        self.speed = speed
        self.color = model.lines[line_name]["color"]
        self.model = model

    @property
    def current_station(self):
        return self.route[self.current_station_idx]

    def process_arrival(self, station):
        """Full implementation of arrival processing"""
        # 1. Unboard passengers
        for passenger in [p for p in self.passengers if p.destination == station]:
            print(
                f"Passenger {passenger.unique_id} disembarking at {station.unique_id}"
            )
            self.passengers.remove(passenger)
            passenger.current_station = station
            station.add_passenger(passenger)

        # 2. Board new passengers going in this train's direction
        # FIXED: Changed 'passenger' to 'p' in the list comprehension
        for passenger in [
            p for p in station.waiting_passengers if self.should_board(p)
        ]:
            if len(self.passengers) < self.capacity:
                print(
                    f"Passenger {passenger.unique_id} boarding at {station.unique_id}"
                )
                station.remove_passenger(passenger)
                passenger.current_train = self
                self.passengers.append(passenger)

    def should_board(self, passenger):
        if not hasattr(passenger, "path"):
            return False
        """Determine if passenger should board this train"""
        # Get all stations on this line
        line_stations = self.model.lines[self.line_name]["stations"]

        # Check if passenger's destination is on this line
        if passenger.destination not in line_stations:
            return False

        # Get passenger's path
        if not passenger.path:
            return False

        # Check if next target in path is reachable via this train
        next_target = passenger.path[0]
        current_station_idx = self.route.index(self.current_station)
        next_station_idx = (current_station_idx + self.direction) % len(self.route)
        next_station = self.route[next_station_idx]

        return next_station == next_target

    def move(self):
        if not self.route or len(self.route) <= 1:
            return

        current = self.current_station
        next_idx = (self.current_station_idx + self.direction) % len(self.route)
        next_station = self.route[next_idx]

        dx = next_station.geometry.x - current.geometry.x
        dy = next_station.geometry.y - current.geometry.y
        dist = (dx**2 + dy**2) ** 0.5

        if dist > 0:
            self.geometry = Point(
                self.geometry.x + dx / dist * self.speed,
                self.geometry.y + dy / dist * self.speed,
            )

        if self.geometry.distance(next_station.geometry) < self.speed:
            self.current_station_idx = next_idx
            self.process_arrival(next_station)

            if self.current_station_idx in (0, len(self.route) - 1):
                self.direction *= -1


class Passenger(mg.GeoAgent):
    def __init__(self, unique_id, origin, destination, model):
        super().__init__(model=model, geometry=origin.geometry, crs="epsg:3857")
        self.unique_id = unique_id
        self.origin = origin
        self.destination = destination
        self.current_station = origin
        self.current_train = None
        self.path = []
        self.model = model
        self.has_path = False
        self.waiting_since = 0  # Просто счетчик шагов ожидания
        origin.add_passenger(self)
        self.find_path()

    def find_path(self):
        """Находит путь между станциями с использованием пересадок"""
        if self.current_station == self.destination:
            self.path = []
            self.has_path = True
            return

        # Проверяем все возможные линии
        possible_lines = []
        for line_name, line_data in self.model.lines.items():
            if self.current_station in line_data["stations"]:
                possible_lines.append(line_name)

        # Проверяем прямые маршруты без пересадок
        for line in possible_lines:
            line_stations = self.model.lines[line]["stations"]
            if self.destination in line_stations:
                self.path = [self.destination]
                self.has_path = True
                return

        # Проверяем маршруты через пересадочные станции
        for transfer in self.model.transfer_stations:
            # Проверяем есть ли путь от текущей до пересадочной
            for line in possible_lines:
                if transfer in self.model.lines[line]["stations"]:
                    # Проверяем есть ли путь от пересадочной до целевой
                    for transfer_line, transfer_data in self.model.lines.items():
                        if (
                            transfer in transfer_data["stations"]
                            and self.destination in transfer_data["stations"]
                        ):
                            self.path = [transfer, self.destination]
                            self.has_path = True
                            return

        self.has_path = False

    def should_board(self, train):
        """Определяет, должен ли пассажир сесть в конкретный поезд"""
        if not self.has_path or not self.path:
            return False

        next_target = self.path[0]
        if next_target in train.route:
            current_position = train.route.index(train.current_station)
            next_position = (current_position + train.direction) % len(train.route)
            return train.route[next_position] == next_target

        return False

    def move(self):
        """Логика перемещения пассажира"""
        if not self.has_path:
            self.find_path()
            if not self.has_path:
                return

        if self.current_station == self.destination:
            return

        if self.current_train:
            # Проверяем нужно ли выходить
            if (
                self.current_train.current_station == self.destination
                or self.current_train.current_station in self.path
            ):

                self.current_train.passengers.remove(self)
                self.current_station = self.current_train.current_station
                self.current_station.add_passenger(self)
                self.current_train = None

                if self.path and self.path[0] == self.current_station:
                    self.path.pop(0)
        else:
            # Ищем подходящий поезд
            next_target = self.path[0] if self.path else None
            if next_target:
                for agent in self.model.grid.agents:
                    if isinstance(agent, Train):
                        if (
                            agent.current_station == self.current_station
                            and next_target in agent.route
                            and len(agent.passengers) < agent.capacity
                            and self.should_board(agent)
                        ):

                            self.current_station.remove_passenger(self)
                            agent.passengers.append(self)
                            self.current_train = agent
                            self.geometry = agent.geometry
                            break


class MetroModel(mesa.Model):
    def __init__(self):
        super().__init__()
        self.grid = mg.GeoSpace()
        self.steps = 0  # Счетчик шагов модели
        self.lines = {
            "Red": {"color": "#ff0000", "stations": []},
            "Blue": {"color": "#0066ff", "stations": []},
            "Green": {"color": "#00aa44", "stations": []},
        }
        self.transfer_stations = []
        self.next_id = 0
        self.build_network()
        self.deploy_trains()

    def build_network(self):
        """Create 3 intersecting metro lines with 2 transfer points"""
        # Red line (horizontal)
        red_coords = [(x, 2) for x in range(0, 6)]
        self.lines["Red"]["stations"] = [
            Station(f"Red_{i}", self, Point(x, y), ["Red"])
            for i, (x, y) in enumerate(red_coords)
        ]

        # Blue line (vertical)
        blue_coords = [(3, y) for y in range(0, 5)]
        self.lines["Blue"]["stations"] = [
            Station(f"Blue_{i}", self, Point(x, y), ["Blue"])
            for i, (x, y) in enumerate(blue_coords)
        ]

        # Green line (diagonal)
        green_coords = [(x, x) for x in range(1, 5)]
        self.lines["Green"]["stations"] = [
            Station(f"Green_{i}", self, Point(x, y), ["Green"])
            for i, (x, y) in enumerate(green_coords)
        ]

        # Create transfer stations
        # Main transfer station (Red and Blue intersection)
        transfer1 = Station("Transfer1", self, Point(3, 2), ["Red", "Blue"])
        transfer1.line_colors = ["#ff0000", "#0066ff"]

        # Secondary transfer (Blue and Green intersection)
        transfer2 = Station("Transfer2", self, Point(3, 3), ["Blue", "Green"])
        transfer2.line_colors = ["#0066ff", "#00aa44"]

        # Replace stations with transfer points
        self.lines["Red"]["stations"][3] = transfer1
        self.lines["Blue"]["stations"][2] = transfer1
        self.lines["Blue"]["stations"][3] = transfer2
        self.lines["Green"]["stations"][2] = transfer2

        self.transfer_stations = [transfer1, transfer2]

        # Connect stations within lines
        for line_name in self.lines:
            stations = self.lines[line_name]["stations"]
            for i in range(len(stations) - 1):
                stations[i].add_connection(stations[i + 1], line_name)
                stations[i + 1].add_connection(stations[i], line_name)

        # Add all stations to grid
        all_stations = []
        for line in self.lines.values():
            all_stations.extend(line["stations"])
        self.grid.add_agents(all_stations)

    def deploy_trains(self):
        """Deploy trains on different lines with varied routes"""
        # Red line express (skips some stations)
        red_line = self.lines["Red"]["stations"]
        red_express_route = [red_line[0], red_line[2], red_line[4]]
        self.grid.add_agents(
            [
                Train(
                    "Red_Express1",
                    self,
                    red_express_route[0].geometry,
                    red_express_route,
                    "Red",
                    speed=0.08,
                ),
                Train(
                    "Red_Express2",
                    self,
                    red_express_route[0].geometry,
                    red_express_route,
                    "Red",
                    speed=0.04,
                ),
                Train(
                    "Red_Express3",
                    self,
                    red_express_route[-1].geometry,
                    list(reversed(red_express_route)),
                    "Red",
                    speed=0.08,
                ),
            ]
        )

        # Blue line circular route
        blue_line = self.lines["Blue"]["stations"]
        blue_circular_route = blue_line + [blue_line[0]]
        self.grid.add_agents(
            [
                Train(
                    "Blue_Circular",
                    self,
                    blue_circular_route[2].geometry,
                    blue_circular_route[2:],
                    "Blue",
                    speed=0.03,
                ),
                Train(
                    "Blue_Circular2",
                    self,
                    blue_circular_route[-1].geometry,
                    list(reversed(blue_circular_route)),
                    "Blue",
                    speed=0.03,
                ),
                Train(
                    "Blue_Circular3",
                    self,
                    blue_circular_route[0].geometry,
                    blue_circular_route,
                    "Blue",
                    speed=0.06,
                ),
            ]
        )

        # Green line bidirectional
        green_line = self.lines["Green"]["stations"]
        self.grid.add_agents(
            [
                Train(
                    "Green_1",
                    self,
                    green_line[0].geometry,
                    green_line,
                    "Green",
                    speed=0.03,
                ),
                Train(
                    "Green_2",
                    self,
                    green_line[-1].geometry,
                    list(reversed(green_line)),
                    "Green",
                    speed=0.03,
                ),
                Train(
                    "Green_3",
                    self,
                    green_line[0].geometry,
                    green_line,
                    "Green",
                    speed=0.06,
                ),
                Train(
                    "Green_4",
                    self,
                    green_line[-1].geometry,
                    list(reversed(green_line)),
                    "Green",
                    speed=0.06,
                ),
            ]
        )

    def step(self):
        self.steps += 1

        # Generate new passengers (5% chance each step)
        if random.random() < 0.05:
            stations = [s for line in self.lines.values() for s in line["stations"]]
            if len(stations) >= 2:
                start, end = random.sample(stations, 2)
                if start != end:
                    passenger = Passenger(
                        unique_id=f"p_{self.next_id}",
                        origin=start,
                        destination=end,
                        model=self,
                    )
                    self.next_id += 1
                    self.grid.add_agents([passenger])

        # Move all agents
        for agent in self.grid.agents:  # Используем grid.agents вместо schedule.agents
            if isinstance(agent, Train) or isinstance(agent, Passenger):
                agent.move()


# Visualization setup
model = MetroModel()
app = dash.Dash(__name__)
app.layout = html.Div(
    [dcc.Graph(id="metro-map"), dcc.Interval(id="tick", interval=1000)]
)


@app.callback(Output("metro-map", "figure"), [Input("tick", "n_intervals")])
def update_map(n):
    model.step()

    # Collect station data
    station_data = []
    for line in model.lines.values():
        for station in line["stations"]:
            station_data.append(
                {
                    "x": station.geometry.x,
                    "y": station.geometry.y,
                    "name": station.unique_id,
                    "color": (
                        station.line_colors[0]
                        if len(station.line_colors) == 1
                        else "#000000"
                    ),
                    "size": 10 + len(station.waiting_passengers),
                    "waiting": len(station.waiting_passengers),
                    "is_transfer": len(station.line_colors) > 1,
                }
            )

    # Process connections between stations
    connections = []
    for line_name, line_data in model.lines.items():
        stations = line_data["stations"]
        for i in range(len(stations) - 1):
            connections.append(
                {
                    "type": "line",
                    "x0": stations[i].geometry.x,
                    "y0": stations[i].geometry.y,
                    "x1": stations[i + 1].geometry.x,
                    "y1": stations[i + 1].geometry.y,
                    "line": {"color": line_data["color"], "width": 2},
                }
            )

    # Process train and passenger data
    train_data = []
    passenger_data = []
    for agent in model.grid.agents:
        if isinstance(agent, Train):
            train_data.append(
                {
                    "x": agent.geometry.x,
                    "y": agent.geometry.y,
                    "name": agent.unique_id,
                    "passengers": len(agent.passengers),
                    "color": agent.color,
                }
            )

            for passenger in agent.passengers:
                passenger_data.append(
                    {
                        "x": agent.geometry.x + random.uniform(-0.05, 0.05),
                        "y": agent.geometry.y + random.uniform(-0.05, 0.05),
                        "status": "on_train",
                        "color": "#FF00FF",
                    }
                )

        elif isinstance(agent, Passenger) and not agent.current_train:
            passenger_data.append(
                {
                    "x": agent.geometry.x + random.uniform(-0.1, 0.1),
                    "y": agent.geometry.y + random.uniform(-0.1, 0.1),
                    "status": "waiting",
                    "color": "#00FF00",
                }
            )

    # Create figure dictionary
    figure = {
        "data": [
            {
                "type": "scatter",
                "x": [s["x"] for s in station_data],
                "y": [s["y"] for s in station_data],
                "text": [
                    f"{s['name']}<br>Waiting: {s['waiting']}" for s in station_data
                ],
                "mode": "markers+text",
                "marker": {
                    "color": [s["color"] for s in station_data],
                    "size": [s["size"] for s in station_data],
                    "symbol": [
                        "star" if s["is_transfer"] else "circle" for s in station_data
                    ],
                },
                "name": "Stations",
                "textposition": "top center",
            },
            {
                "type": "scatter",
                "x": [t["x"] for t in train_data],
                "y": [t["y"] for t in train_data],
                "text": [
                    f"{t['name']}<br>Passengers: {t['passengers']}" for t in train_data
                ],
                "mode": "markers",
                "marker": {
                    "color": [t["color"] for t in train_data],
                    "size": [15 + t["passengers"] for t in train_data],
                    "symbol": "square",
                },
                "name": "Trains",
            },
            {
                "type": "scatter",
                "x": [p["x"] for p in passenger_data],
                "y": [p["y"] for p in passenger_data],
                "mode": "markers",
                "marker": {
                    "color": [p["color"] for p in passenger_data],
                    "size": 8,
                    "symbol": "circle",
                },
                "name": "Passengers",
                "hoverinfo": "text",
                "hovertext": [f"Status: {p['status']}" for p in passenger_data],
            },
        ],
        "layout": {
            "shapes": connections,
            "title": f"Metro Simulation (Step: {model.steps})",
            "hovermode": "closest",
            "showlegend": True,
            "xaxis": {"range": [-1, 6]},  # Adjust based on your coordinate system
            "yaxis": {"range": [-1, 6]},  # Adjust based on your coordinate system
        },
    }

    return figure


if __name__ == "__main__":
    app.run(debug=True)
