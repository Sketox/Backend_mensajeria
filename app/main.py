from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import socketio
from app.socket_manager import UserManager, EventObserver
from app.fcm import send_notification

import os
import firebase_admin
from firebase_admin import credentials

# Inicializa Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(
            os.path.dirname(__file__),
            "config/firebase/mensajeriaconnotis-firebase-adminsdk-fbsvc-89af2d4e8c.json"
        )
    )
    firebase_admin.initialize_app(cred)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
socket_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")
app.mount("/ws", socket_app)

user_manager = UserManager()
observer = EventObserver()

# Observer para notificaciones FCM y eventos en tiempo real
def fcm_listener(event, data):
    if event == "new_message":
        send_notification(data["username"], data["message"])
    elif event == "user_joined":
        send_notification("Nuevo usuario", f"{data['username']} se ha unido al chat")

observer.subscribe(fcm_listener)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Servidor backend de chat en FastAPI</h1>"

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def join(sid, data):
    username = data.get("username")
    user_manager.add_user(sid, username)
    await sio.emit("update_users", user_manager.get_users())
    observer.notify("user_joined", {"username": username})

@sio.event
async def message(sid, data):
    username = user_manager.get_username(sid)
    msg_data = {"username": username, "message": data["message"]}
    await sio.emit("new_message", msg_data)
    observer.notify("new_message", msg_data)

@sio.event
async def disconnect(sid):
    user_manager.remove_user(sid)
    await sio.emit("update_users", user_manager.get_users())
    print("Client disconnected:", sid)

# Diccionario para guardar tokens por usuario (en memoria, para pruebas)
user_tokens = {}

@app.post("/register_token")
async def register_token(request: Request):
    data = await request.json()
    username = data.get("username")
    token = data.get("token")
    print(f"[FCM] Registrando token para usuario: {username} -> {token}")
    if username and token:
        user_tokens[username] = token
        print(f"[FCM] Tokens actuales: {user_tokens}")
        return {"status": "ok"}
    print("[FCM] Error: Faltan username o token")
    return {"status": "error", "detail": "Missing username or token"}

