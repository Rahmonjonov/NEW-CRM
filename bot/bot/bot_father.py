import telebot
import requests
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

TOKEN = None

url = "http://crm.backoffice.uz/board/"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    res = requests.get(url + "telegram_bot_get_company/?token={}&chat_id={}".format(TOKEN, message.chat.id))
    data = res.json()
    rkm = ReplyKeyboardMarkup(True)
    rkm.add(KeyboardButton('O\'z telefon raqamingizni yuboring', request_contact=True))
    bot.send_message(message.chat.id, "{} kompaniyasiga hush kelibsiz".format(data['company']['name']))
    bot.send_message(message.from_user.id, 'O\'z telefon raqamingizni yuboring!', reply_markup=rkm)


@bot.message_handler(content_types=['contact'])
def get_contact(message):
    phone = message.contact.phone_number
    res = requests.get(url+"telegram_bot_add_phone/?token={}&chat_id={}&phone={}".format(TOKEN, message.chat.id, phone))
    bot.send_message(message.from_user.id, 'Familiya va ismingizni yozing')




@bot.message_handler(func=lambda message: True)
def echo_all(message):
    res = requests.get(url + "telegram_bot_get_company/?token={}&chat_id={}".format(TOKEN, message.chat.id))
    data = res.json()
    if data['user']['step'] == 2:
        res = requests.get(url+"telegram_bot_add_name/?token={}&chat_id={}&name={}".format(TOKEN, message.chat.id, message.text))
        if res.ok:
            bot.send_message(message.chat.id,"Kompanyangiz nomi")
    elif data['user']['step'] == 3:
        res = requests.get(
            url + "telegram_bot_add_company/?token={}&chat_id={}&company={}".format(TOKEN, message.chat.id, message.text))
        if res.ok:
            bot.send_message(message.chat.id, "Kompanyangiz manzili")
    elif data['user']['step'] == 4:
        res = requests.get(
            url + "telegram_bot_add_company_address/?token={}&chat_id={}&companyaddress={}".format(TOKEN, message.chat.id, message.text))
        if res.ok:
            dt = res.json()
            res_finish = requests.post(url+"create_lead_by_tg/",data={
                "name":dt['user']['name'],
                "company":dt['user']['company'],
                "address":dt['user']['companyAddress'],
                "phone":dt['user']['phone'],
                "token":TOKEN,
                "tg_chatid":message.chat.id,
            })
            if res_finish.ok:
                bot.send_message(message.chat.id,
                                 "Muvofaqqiyatli ro'yhatdan o'tdingiz. Tez orada operatorlarimiz siz bilan bog'lanadi!")
    else:
        bot.reply_to(message, "Xabar qoldirganingiz uchun raxmat.\nTez orada operatorlarimiz siz bilan bog'lanadi!")


bot.polling()
