from celery import shared_task
import requests
from account.models import Company
import logging
logger = logging.getLogger(__name__)

@shared_task
def send_to_bot(text, bot_token, group_id, user_tg_id):
    try:
        token = bot_token
        chat_id = group_id
        url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
        results = requests.get(url_req)

        url_req1 = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user_tg_id + "&text=" + text
        results1 = requests.get(url_req1)
    except Exception as e:
        print(f"Error in send_to_bot task: {e}")

    
# send_to_bot('12334')