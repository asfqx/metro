# 🛤️ Модель метрополитена на FastAPI

## 📌 Назначение программы

Система моделирует работу метрополитена:

- Станции и линии метро связаны между собой.
- Поезда следуют по линиям и могут находиться на станциях.
- Пассажиры имеют начальную и конечную станции, могут перемещаться и менять статус (`ожидает`, `в поезде`, `прибыл`).
- Через WebSocket можно получать и отправлять данные в реальном времени.
- REST API предоставляет доступ к текущей информации о моделируемых объектах.

---

## 🧰 Используемые технологии и их назначение

| Технология                 | Назначение                                                                 |
|---------------------------|---------------------------------------------------------------------------|
| **FastAPI**               | Основной web-фреймворк. Обрабатывает REST API и WebSocket маршруты.       |
| **uvicorn**               | ASGI-сервер для запуска FastAPI приложения.                              |
| **SQLAlchemy (v2)**       | ORM для описания моделей (`Passenger`, `Station`, `Train`, `Line`)        |
| **Pydantic Settings**     | Загрузка конфигурации (параметры подключения к БД) из `config.py`.        |
| **PostgreSQL**            | Используемая реляционная база данных, подключение через `asyncpg`.        |
| **httpx**                 | Асинхронный HTTP-клиент для внутренних запросов (например, при старте WebSocket-сессии). |
| **WebSocket (FastAPI)**   | Для двусторонней связи с клиентом. |
| **Enum** (`Status`)       | Перечисление возможных состояний пассажира: `WAITING`, `IN_TRAIN`, `FINISHED`. |

---

## 🧱 Структура моделей

- **Line** — линия метро. Имеет имя, станции на маршруте (`route`) и список поездов.
- **Station** — станция метро. Принадлежит линии, имеет вместимость и список пассажиров.
- **Train** — поезд. Имеет вместимость, текущую станцию и линию, по которой следует.
- **Passenger** — пассажир. Имеет начальную и конечную станции, может быть на станции или в поезде.
- **Status** — статус пассажира: ожидание, в пути, прибыл.

---

## 🔌 WebSocket

- `/ws` — WebSocket-соединение, по подключению отправляет стартовые данные и может принимать команды обновления.

---

## ⚙️ Пример работы приложения

- При старте FastAPI вызывает `setup_database()` — инициализация подключения к БД.
- Клиент подключается к `/ws`, получает стартовые данные и может отправлять команды.
- Вся модель работает в асинхронном режиме.
