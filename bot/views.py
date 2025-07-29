import os
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from board.models import Lead, NewComplaints
import requests

TOKEN = '8237800951:AAERJeLeCWQ6NQCMcGrJ6YiZyl0B1vjTsb8'
URL = f'https://api.telegram.org/bot{TOKEN}/'


user_states = {}  

def send_message(chat_id, text, reply_markup=None):
    data = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': reply_markup,
        'parse_mode': 'HTML'
    }
    requests.post(URL + 'sendMessage', json=data)

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')

        contact = message.get('contact')
        text = message.get('text', '').strip()

        if contact:
            phone = contact.get('phone_number')
            try:
                lead = Lead.objects.filter(phone=phone).last()
                user_states[chat_id] = {"phone": phone}
                send_message(chat_id, "✅ Raqamingiz tasdiqlandi.")
                send_menu(chat_id)
            except Lead.DoesNotExist:
                send_message(chat_id, "❌ Bu raqam bazada mavjud emas.")
        
        elif text == "/start":
            if chat_id not in user_states:
                keyboard = {
                    "keyboard": [[
                        {
                            "text": "📱 Raqamni yuborish",
                            "request_contact": True
                        }
                    ]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True
                }
                send_message(chat_id, "Iltimos, raqamingizni yuboring:", reply_markup=keyboard)
            else:
                send_menu(chat_id)

        elif text == "📝 Shikoyat yozish":
            if chat_id in user_states:
                user_states[chat_id]["waiting_for_complaint"] = True
                send_message(chat_id, "Shikoyatingizni yozing:")
            else:
                send_message(chat_id, "Iltimos, avval raqamingizni yuboring.")

        elif chat_id in user_states and user_states[chat_id].get("waiting_for_complaint"):
            phone = user_states[chat_id]["phone"]
            try:
                lead = Lead.objects.filter(phone=phone).last()
                NewComplaints.objects.create(
                    lead=lead,
                    complaint=text,
                    is_bot=True
                )
                user_states[chat_id]["waiting_for_complaint"] = False
                send_message(chat_id, "✅ Shikoyatingiz qabul qilindi.")
                send_menu(chat_id)
            except Lead.DoesNotExist:
                send_message(chat_id, "❌ Raqam topilmadi.")

        return JsonResponse({"ok": True})
    return JsonResponse({"message": "Webhook ishlayapti"}, status=200)

def send_menu(chat_id):
    keyboard = {
        "keyboard": [[
            {"text": "📝 Shikoyat yozish"},
        ]],
        "resize_keyboard": True
    }
    send_message(chat_id, "Menyudan tanlang:", reply_markup=keyboard)




def add_bot(request):
    token = request.POST.get('token')
    user_id = request.user.id
    comp = request.user.company
    comp.tg_token = token
    comp.save()
    bot_path = str(settings.BASE_DIR)+'/bot/bot/bot_father.py'
    bot_new = f'/bot/bots/bot_{user_id}.py'.format(user_id)
    bot_conf = str(settings.BASE_DIR)+"/bot/conf/bot_conf.conf"
    bot_conf_new = "/etc/supervisor/conf.d/bot_conf_{}.conf".format(user_id)

    with open(bot_path) as f:
        newText = f.read().replace('TOKEN = None', 'TOKEN = "'+token+'"')

    with open(bot_new, "w") as f:
        f.write(newText)

    with open(bot_conf) as f:
        newText = f.read().replace('[program:bot]', '[program:bot_{}]'.format(user_id))
        newText = newText.replace('command=/bot/venv/bin/python /bot/bots/bot_father.py', 'command=/bot/venv/bin/python /bot/bots/bot_{}.py'.format(user_id))

    with open(bot_conf_new, "w") as f:
        f.write(newText)

    os.system("supervisorctl reread")
    os.system("supervisorctl update")
    os.system("supervisorctl restart bot_{}".format(user_id))

    return redirect('setting')

