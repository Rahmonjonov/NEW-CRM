import os
from django.conf import settings
from django.shortcuts import redirect

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

