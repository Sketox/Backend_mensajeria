import socketio
from app.fcm import send_notification

sio = socketio.AsyncServer(async_mode="asgi")

connected_users = {}

@sio.event
async def connect(sid, environ):
    print("Cliente conectado:", sid)

@sio.event
async def disconnect(sid):
    print("Cliente desconectado:", sid)
    if sid in connected_users:
        del connected_users[sid]

@sio.event
async def join(sid, data):
    username = data["username"]
    connected_users[sid] = username
    print(f"{username} se ha unido al chat")

@sio.event
async def message(sid, data):
    username = connected_users.get(sid, "Anónimo")
    msg = data["message"]

    await sio.emit("new_message", {
        "username": username,
        "message": msg
    })

    await send_notification(f"Nuevo mensaje de {username}", msg)
