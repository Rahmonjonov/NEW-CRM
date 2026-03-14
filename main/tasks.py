from celery import shared_task
import requests
from account.models import Company
import logging
logger = logging.getLogger(__name__)
print('uuuu')
# @shared_task
# def send_to_bot(text, bot_token, group_id, user_tg_id=None):
#     try:
#         token = bot_token
#         chat_id = group_id
#         url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
#         results = requests.get(url_req)
#         print(results, 'aaaaaa')
#         if user_tg_id:
#             url_req1 = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user_tg_id + "&text=" + text
#             results1 = requests.get(url_req1)
#     except Exception as e:
#         print(f"Error in send_to_bot task: {e}")


@shared_task
def send_to_bot(text, bot_token, group_id, user_tg_id=None, parse_mode="Markdown"):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # Guruhga yuborish
        payload = {
            "chat_id": group_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        response = requests.post(url, data=payload)
        print("Group response:", response.text)  # <-- natijani ko‘r

        # Agar user_tg_id berilgan bo‘lsa unga ham yuborish
        if user_tg_id:
            payload["chat_id"] = user_tg_id
            response2 = requests.post(url, data=payload)
            print("User response:", response2.text)

    except Exception as e:
        print(f"Error in send_to_bot task: {e}")

# send_to_bot('aaaa', '6768544241:AAGzvhOPWHS88bT5VNDoGVjm_2j4UEzf_IM', '-4919621071')
# send_to_bot('12334')