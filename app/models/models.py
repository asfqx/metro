import mesa_geo as mg
from shapely.geometry import Point
from .metromodel import MetroModel
from collections import defaultdict


class Station(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, line, line_colors=None):
        super().__init__(model=model, geometry=geometry, crs="epsg:3857")
        self.unique_id = unique_id
        self.line_colors = line_colors if line_colors else ["#000000"]
        self.waiting_passengers = []
        self.connections = defaultdict(list)  # {line_name: [connected_stations]}
        self.line = line
        self.capacity = 100 - len(self.waiting_passengers)

    def add_passenger(self, passenger):
        if self.capacity != 0:
            self.waiting_passengers.append(passenger)
            self.capacity -= 1

    def remove_passenger(self, passenger):
        if passenger in self.waiting_passengers:
            self.waiting_passengers.remove(passenger)
            self.capacity += 1

    def add_connection(self, station, line_name):
        if station not in self.connections[line_name]:
            self.connections[line_name].append(station)


class Train(mg.GeoAgent):
    def __init__(
        self, unique_id, model: MetroModel, geometry, route, line_name, speed=0.05
    ):
        super().__init__(model=model, geometry=geometry, crs="epsg:3857")
        self.unique_id = unique_id
        self.route = route
        self.line_name = line_name
        self.current_station_idx = 0
        self.direction = 1  # 1 forward, -1 backward
        self.passengers = []
        self.capacity = 100 - len(self.passengers)
        self.speed = speed
        self.color = model.lines[line_name]["color"]

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
        """Determine if passenger should board this train"""
        # Get all stations on this line
        line_stations = self.model.lines[self.line_name]["stations"]

        # Check if passenger's destination is on this line
        if passenger.destination not in line_stations:
            return False

        # Get passenger's path
        if not passenger.path:
            return False

        return True

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
    def __init__(self, unique_id, origin, destination, model: MetroModel):
        super().__init__(model=model, geometry=origin.geometry, crs="epsg:3857")
        self.unique_id = unique_id
        self.origin: Station = origin
        self.destination: Station = destination
        self.current_station: Station = origin
        self.current_train = None
        self.path = []
        self.model = model
        self.has_path = False
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
