from pyfcm import FCMNotification
from dotenv import load_dotenv
import os

load_dotenv()
fcm_key = os.getenv("FCM_SERVER_KEY")

push_service = FCMNotification(api_key=fcm_key)

async def send_notification(title, body):
    result = push_service.notify_topic_subscribers(
        topic_name="chat_general",
        message_title=title,
        message_body=body
    )
    print("Notificación enviada:", result)
