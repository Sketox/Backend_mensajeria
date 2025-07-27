import socketio
from app.fcm import send_notification
from typing import List, Callable, Dict, Any

sio = socketio.AsyncServer(async_mode="asgi")

# Singleton para manejo de usuarios conectados
class UserManager:
    _instance = None
    _users: Dict[str, str] = {}  # sid -> username

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
        return cls._instance

    def add_user(self, sid: str, username: str):
        self._users[sid] = username

    def remove_user(self, sid: str):
        if sid in self._users:
            del self._users[sid]

    def get_users(self) -> List[str]:
        return list(self._users.values())

    def get_username(self, sid: str) -> str:
        return self._users.get(sid, "Anónimo")

# Observer para eventos
class EventObserver:
    def __init__(self):
        self._listeners: List[Callable[[str, Any], None]] = []

    def subscribe(self, listener: Callable[[str, Any], None]):
        self._listeners.append(listener)

    def notify(self, event: str, data: Any):
        for listener in self._listeners:
            listener(event, data)

connected_users = UserManager()
event_observer = EventObserver()

@sio.event
async def connect(sid, environ):
    print("Cliente conectado:", sid)

@sio.event
async def disconnect(sid):
    print("Cliente desconectado:", sid)
    connected_users.remove_user(sid)

@sio.event
async def join(sid, data):
    username = data["username"]
    connected_users.add_user(sid, username)
    print(f"{username} se ha unido al chat")

@sio.event
async def message(sid, data):
    username = connected_users.get_username(sid)
    msg = data["message"]

    await sio.emit("new_message", {
        "username": username,
        "message": msg
    })

    await send_notification(f"Nuevo mensaje de {username}", msg)
