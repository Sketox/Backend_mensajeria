from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import socketio
from app.socket_manager import sio

app = FastAPI()

# CORS: Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a ["http://localhost:3000"] si usas React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar Socket.IO sobre FastAPI
app.mount("/", socketio.ASGIApp(sio, other_asgi_app=app))

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Servidor backend de chat en FastAPI</h1>"
