from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import socketio
from app.socket_manager import sio

import os
import firebase_admin
from firebase_admin import credentials, messaging

# Inicializa Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(
            os.path.dirname(__file__),
            "config/firebase/mensajeriaconnotis-firebase-adminsdk-fbsvc-89af2d4e8c.json"
        )
    )
    firebase_admin.initialize_app(cred)

app = FastAPI()

# CORS: Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a ["http://localhost:3000"] si usas React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar Socket.IO sobre FastAPI en una ruta diferente
sio_app = socketio.ASGIApp(sio)
app.mount("/ws", sio_app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Servidor backend de chat en FastAPI</h1>"

@app.post("/send-message/")
async def send_message(token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )
    try:
        response = messaging.send(message)
        return {"message": f"Mensaje enviado con éxito: {response}"}
    except Exception as e:
        return {"error": str(e)}
