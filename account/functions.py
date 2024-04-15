from datetime import datetime, timedelta

import requests

from account.models import Invoice

invoice_expire_time = timedelta(days=30)


def create_invoice(company):
    created = False
    if company.plan is not None:
        if company.plan.price <= company.balance:
            Invoice.objects.create(company_id=company.id,
                                   start=datetime.now(),
                                   end=datetime.now() + invoice_expire_time,
                                   plan=company.plan,
                                   summa=company.plan.price,
                                   active=True)
            company.balance -= company.plan.price
            company.active = True
            company.save()
            created = True
    return created


def check_one_company_invoice(company):
    try:
        Invoice.objects.filter(end__lt=datetime.now(), active=True, company=company).update(active=False)
        bor = Invoice.objects.filter(end__gt=datetime.now(), company=company).count() > 0
        if not bor and company.active:
            company.active = False
            company.save()
        elif bor and not company.active:
            company.active = True
            company.save()
        if not company.active:
            create_invoice(company)
    except:
        pass


sms_special_name = "{{ism}}"
sms_special_phone = "{{tel}}"


def sms_text_replace(sms_text, lead):
    try:
        sms_text = str(sms_text).replace(sms_special_name, lead.name)
    except:
        pass
    try:
        sms_text = str(sms_text).replace(sms_special_phone, lead.phone)
    except:
        pass
    return sms_text


def checkPhone(phone):
    try:
        int(phone)
        if len(phone) == 12:
            return True, phone
        else:
            return False, None
    except:
        return False, None


def sendSmsOneContact(company, phone, message):
    result = requests.post(url="http://notify.eskiz.uz/api/message/sms/send",
                           headers={'Authorization': f'Bearer {company.sms_token}'},
                           data={
                               "mobile_phone": phone,
                               "message": message,
                               "from": company.sms_from,
                               "callback_url": company.sms_callback_url
                           })
    return result


def sendSmsOneContact_from_sms_to(company, phone, message):
    result = requests.post(url="https://api.sms.to/sms/send",
                           headers={'Authorization': f'Bearer {company.smsto_token}'},
                           data={
                               "to": phone,
                               "message": message,
                               "bypass_optout": True,
                               "sender_id": company.smsto_sender_id,
                           })
    return result
