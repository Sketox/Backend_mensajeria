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

def send_notification(title, body):
    from app.main import user_tokens  # Importa aquí para evitar import circular
    tokens = list(user_tokens.values())
    print(f"[FCM] Enviando notificación a tokens: {tokens}")
    if not tokens:
        print("[FCM] No hay tokens registrados.")
        return
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        try:
            response = messaging.send(message)
            print(f"[FCM] Notificación enviada a {token}: {response}")
        except Exception as e:
            print(f"[FCM] Error al enviar a {token}: {e}")
