import json
import random
import dash
import websockets
from dash import dcc, html
from dash.dependencies import Input, Output
from fastapi import Depends
from .models.models import Train, Passenger
from .models.metromodel import MetroModel


async def connect_websocket():
    url = "ws://localhost:8081/ws"
    while True:
        async with websockets.connect(url) as websocket_session:
            status = {
                "status": "success connected",
            }
            await websocket_session.send(json.dumps(status))
            yield websocket_session


async def websocket_get_update(session=Depends(connect_websocket)):
    status = {
        "status": "get_update",
    }
    await session.send(json.dumps(status))
    data = await session.recv()
    return json.loads(data)


async def websocket_send_update(data, session=Depends(connect_websocket)):
    status = {"status": "update"}
    await session.send(json.dumps(status))
    await session.send(json.dumps(data))
    print("data successfully load to db")


model = MetroModel(data=websocket_get_update())
app = dash.Dash(__name__)
app.layout = html.Div(
    [dcc.Graph(id="metro-map"), dcc.Interval(id="tick", interval=1000, n_intervals=0)]
)


@app.callback(Output("metro-map", "figure"), [Input("tick", "n_intervals")])
async def update_map(n):
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

            for _ in agent.passengers:
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
    data = {
        "data": [model.trains, model.passengers, model.stations],
    }
    await websocket_send_update(data)
    return figure


if __name__ == "__main__":
    app.run(debug=True)
