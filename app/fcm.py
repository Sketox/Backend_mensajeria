from firebase_admin import messaging, credentials, initialize_app
import firebase_admin
import os

# Inicializa Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(
            os.path.dirname(__file__),
            "config/firebase/mensajeriaconnotis-firebase-adminsdk-fbsvc-89af2d4e8c.json"
        )
    )
    initialize_app(cred)

async def send_notification(title, body, token=None, topic="chat_general"):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token,
        topic=topic if token is None else None
    )
    response = messaging.send(message)
    print("Notificación enviada:", response)
    return response
