from datetime import datetime

import requests
from django.conf import settings
from django.http import HttpResponse

from account.functions import create_invoice, sms_text_replace, checkPhone, sendSmsOneContact, \
    sendSmsOneContact_from_sms_to
from account.models import Company, Invoice, Card, Company_default_poles
from board.models import Lead, LeadPoles, SMSTemplate, SMSHistory, SMS_template_choise
from orders.models import Order

merchan_id = settings.PAYCOM_MERCHANT_ID
secret_key = settings.PAYCOM_API_KEY
# payme_url = "https://checkout.test.paycom.uz/api"
payme_url = "https://checkout.paycom.uz/api"


def create_invoice_for_company(company):
    created = create_invoice(company)
    if not created:
        receipt_create_and_pay_for_company(company_id=company.id)


def check_company_invoice():
    # invoice deactive
    Invoice.objects.filter(end__lt=datetime.now(), active=True).update(active=False)

    # companies activate and deactive
    companies = Company.objects.all()
    comps_invoices = Invoice.objects.filter(end__gt=datetime.now())
    for company in companies:
        bor = False
        for invoice in comps_invoices:
            if invoice.company == company:
                bor = True
                break
        if not bor and company.active:
            company.active = False
            company.save()
        elif bor and not company.active:
            company.active = True
            company.save()

    # create invoice and active company
    companies = companies.filter(active=False)
    for company in companies:
        create_invoice_for_company(company)


def check_company(request):
    check_company_invoice()

    resp = '<h1>Done</h1>'
    # if request.GET.get('create_lead_pole') == '5':
    #     create_lead_pole_companies()
    #     resp = 'create_lead_pole done'
    #
    # if request.GET.get('change_lead_to_pole') == '5':
    #     change_lead_to_lead_poles()
    #     resp = 'change_lead_to_pole done'
    return HttpResponse(resp)


def receipt_create_and_pay_for_company(company_id):
    company = Company.objects.get(id=company_id)

    if not company.active and check_no_wait_order(company_id) and company.plan is not None:
        try:
            pay_summa = (company.plan.price - company.balance) * 100
            card = Card.objects.get(company_id=company_id)
            if card.active:
                order = Order.objects.create(company_id=company_id, amount=pay_summa,
                                             state=Order.ORDER_ON_WAIT, card=card.number)
                response = receipt_create(pay_summa, order)
                if "result" in response.json():
                    if "receipt" in response.json()['result']:
                        tranzaction_id = response.json()['result']['receipt']['_id']
                        receipt_pay(tranzaction_id, card)
                if "error" in response.json():
                    order.delete()

        except Card.DoesNotExist:
            pass
        except:
            pass


def check_no_wait_order(company_id):
    return Order.objects.filter(company_id=company_id, state=1).count() == 0


def receipt_create(pay_summa, order):
    data = {
        "method": "receipts.create",
        "params": {
            "amount": pay_summa,
            "account": {
                "order_id": order.id
            }
        }
    }
    headers = {
        'X-Auth': f'{merchan_id}:{secret_key}'
    }
    return requests.post(payme_url,
                         json=data,
                         headers=headers
                         )


def receipt_pay(tranzaction_id, card):
    return requests.post(payme_url,
                         json={
                             "method": "receipts.pay",
                             "params": {
                                 "id": tranzaction_id,
                                 "token": card.token,
                             }
                         },
                         headers={
                             'X-Auth': merchan_id + ":" + secret_key
                         }
                         )


def create_lead_pole_companies():
    companies = Company.objects.all()
    for company in companies:
        if LeadPoles.objects.filter(company=company).count() == 0:

            for i in Company_default_poles:
                LeadPoles.objects.create(
                    name=i[0],
                    status=i[1],
                    company=company
                )


def change_lead_to_lead_poles():
    companies = Company.objects.all()
    for company in companies:
        leads = Lead.objects.filter(is_active=True, created_user__company=company)
        leadpoles = LeadPoles.objects.filter(company=company)
        for lead in leads:
            lead.pole = get_pole(lead.status, leadpoles)
            lead.save()


def get_pole(status, lead_poles):
    for i in lead_poles:
        if i.status == status:
            return i


def schedular_sms_send():
    templates = SMSTemplate.objects.filter(
        active=True, company__active=True, type=SMS_template_choise[2][0],
        date=datetime.now().date()
    )
    for template in templates:
        success_send_count = 0
        error_send_count = 0
        if template.company.sms_activated:
            for lead in template.leads.all():
                text = sms_text_replace(template.text, lead)
                can, phone = checkPhone(lead.phone)
                if can:
                    result = sendSmsOneContact(template.company, lead.phone, text)
                    if result.status_code == 200:
                        success_send_count += 1
                    else:
                        error_send_count += 1
                else:
                    error_send_count += 1
        elif template.company.smsto_activated:
            for lead in template.leads.all():
                text = sms_text_replace(template.text, lead)
                result = sendSmsOneContact_from_sms_to(template.company, lead.phone, text)
                if result.status_code == 200:
                    success_send_count += 1
                else:
                    error_send_count += 1

        template.active = False

        is_success = success_send_count == template.leads.count()
        SMSHistory.objects.create(smstemplate=template,
                                  date=template.date,
                                  is_success=is_success,
                                  send_count=success_send_count,
                                  not_send_count=error_send_count
                                  )


def get_lead_template(templates, lead: Lead):
    for template in templates:
        if lead.created_user.company == template.company:
            return True, template

    return False, None


def birthday_sms_send():
    vaqt = datetime.now().date()
    leads = Lead.objects.filter(
        is_active=True,
        birthday__day=vaqt.day,
        birthday__month=vaqt.month,
        sms_send=False)

    templates = SMSTemplate.objects.filter(
        active=True, company__active=True, type=SMS_template_choise[1][0]
    )

    for lead in leads:
        isset, template = get_lead_template(templates, lead)
        if isset:
            if template.company.sms_activated:
                can, phone = checkPhone(lead.phone)
                if can:
                    text = sms_text_replace(template.text, lead)
                    result = sendSmsOneContact(template.company, lead.phone, text)
                    if result.status_code == 200:
                        lead.sms_send = True
                        lead.save()
            elif template.company.smsto_activated:
                text = sms_text_replace(template.text, lead)
                result = sendSmsOneContact_from_sms_to(template.company, lead.phone, text)
                if result.status_code == 200:
                    lead.sms_send = True
                    lead.save()

    Lead.objects \
        .exclude(birthday__day=vaqt.day, birthday__month=vaqt.month) \
        .filter(sms_send=True) \
        .update(sms_send=False)
    refresh_sms_token()
    refresh_smsto_token()


def refresh_sms_token():
    url = 'http://notify.eskiz.uz/api/auth/login'
    url_get_info = 'http://notify.eskiz.uz/api/auth/user'
    companyes = Company.objects.filter(active=True, sms_activated=True)
    for company in companyes:
        response = requests.post(url, data={
            "email": company.sms_email,
            "password": company.sms_password,
        })
        if response.status_code == 200:
            company.sms_token = response.json()['data']['token']
            response2 = requests.get(url_get_info, headers={
                "Authorization": f"Bearer {company.sms_token}",
            })
            if response2.status_code == 200:
                company.sms_balans = response2.json()['data']['balance']

            company.save()


def refresh_smsto_token():
    companyes = Company.objects.filter(active=True, smsto_activated=True)
    for company in companyes:
        response = requests.post('https://auth.sms.to/oauth/token', data={
            "client_id": company.smsto_client_id,
            "secret": company.smsto_secret,
            "expires_in": company.smsto_expires_in,
        })
        if response.status_code == 200:
            company.smsto_token = response.json()['jwt']
            company.smsto_activated = True
        else:
            company.smsto_activated = False
        company.save()
