from django.utils import translation

class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.COOKIES.get('django_language'):
            translation.activate('uz')
            request.LANGUAGE_CODE = 'uz'
        response = self.get_response(request)
        translation.deactivate()
        return response
    


import re
from board.models import LastSeen

URL_PATTERNS = [
    (r"^/goal/add_goal(/|$)", 'Maqsad qo‘shildi'),
    (r"^/goal(/|$)", 'Maqsad boʻlimi'),
    (r"^/cabinet(/|$)", 'Kabinet boʻlimi'),
    (r"^/register(/|$)", 'Roʻyxatdan oʻtish'),
    (r"^/companyCard(/|$)", "Karta qoʻshish"),
    (r"^/edit_company(/|$)", "Kompaniyani tahrirlash"),
    (r"^/app-calendar(/|$)", "Kalendar boʻlimi"),
    (r"^/setting(/|$)", "Sozlamalar boʻlimi"),
    (r"^/edit(/|$)", "Mijoz tafsiloti"),
    (r"^/add_task_with_lead/\d+(/|$)", "Mijoz orqali vazifa qoʻshish"),
    (r"^/up(/|$)", "Promouterga oʻtkazish"),
    (r"^/delete_lead(/|$)", "Mijozni oʻchirish"),
    (r"^/target(/|$)", "Target boʻlimi"),
    (r"^/clients(/|$)", "Mijozlar bazasi boʻlimi"),
    (r"^/sms(/|$)", "SMS boʻlimi"),
    (r"^/smsgateway(/|$)", "SMS qoʻshildi"),
    (r"^/etiroz(/|$)", "Savdo boʻlimi"),
    (r"^/objectionwrite(/|$)", "Eʻtiroz qoʻshildi"),
    (r"^/object(/|$)", "Tez-tez takrorlanadigan eʻtirozlar va javoblar qoʻshildi"),
    (r"^/delete(/|$)", "Tez-tez takrorlanadigan eʻtirozlar va javoblar oʻchirildi"),
    (r"^/edito(/|$)", "Tez-tez takrorlanadigan eʻtirozlar va javoblar tahrirlandi"),
    (r"^/adduser(/|$)", "Mijoz qo‘shildi"),
    (r"^/debt(/|$)", "Qarzdorlik boʻlimi"),
    (r"^/hodim(/|$)", "Xodimlar boʻlimi"),
    (r"^/calenedit(/|$)", "Taqvimni tahrirlash boʻlimi"),
    (r"^/caleneditform(/|$)", "Hodisa Tahrirlash boʻlimi"),
    (r"^/calendel(/|$)", "Taqvimni oʻchirildi"),
    (r"^/saveeditcalen(/|$)", "Hodisa tahrirlandi"),
    (r"^/addnotes(/|$)", "Xulosa qoʻshildi"),
    (r"^/debthistory(/|$)", "Qarz tarixi boʻlimi"),
    (r"^/adddebt(/|$)", "Qarz qoʻshildi"),
    (r"^/editspin(/|$)", "Spin tahrirlandi"),
    (r"^/postevent(/|$)", "Taqvim qoʻshildi"),
    (r"^/delevent(/|$)", "Taqvim oʻchirildi"),
    (r"^/editevent(/|$)", "Taqvim tahrirlandi"),
    (r"^/addhodim(/|$)", "Xodim qoʻshildi"),
    (r"^/deletehodim(/|$)", "Xodim oʻchirildi"),
    (r"^/importLead(/|$)", "Mijoz import qilindi"),
    (r"^/addtoken(/|$)", "Xodimga token qo‘shildi"),
    (r"^/addsms(/|$)", "Kompaniyaga SMS qo‘shildi"),
    (r"^/addsmsto(/|$)", "Kompaniyaga SMS token qo‘shildi"),
    (r"^/edituser(/|$)", "Mijoz tahrirlandi"),
    (r"^/edithodim(/|$)", "Xodim tahrirlandi"),
    (r"^/products(/|$)", "Mahsulotlar"),
    (r"^/add_product(/|$)", "Mahsulot qo‘shildi"),
    (r"^/search_lead(/|$)", "Mijoz izlandi"),
    (r"^/edit_referall(/|$)", "Yo'naltirish tahrirlandi"),
    (r"^/add_referall(/|$)", "Yo'naltirish qo‘shildi"),
    (r"^/del_referall(/|$)", "Yo'naltirish oʻchirildi"),
    (r"^/notes_ping(/|$)", "Mijoz xulosasi ping qilindi"),
    (r"^/edit_userleadpoles(/|$)", "Mo’ljaldagi potensiallar"),
    (r"^/call_logs(/|$)", "Qo‘ng‘iroqlar jurnali"),
    (r"^/add-moizvonki(/|$)", "Mening qo'ng'iroqlarim"),
    (r"^/add_new_complaint(/|$)", "Yangi shikoyat qo‘shildi"),
    (r"^/edit_new_complaint/\d+(/|$)", "Shikoyatni tahrirlash"),
    (r"^/del_new_complaint/\d+(/|$)", "Shikoyatni oʻchirildi"),
    (r"^/change_status_new_complaint(/|$)", "Shikoyatni holatni o‘zgartirildi"),
    (r"^/add_new_objections(/|$)", "Yangi etiroz qo‘shildi"),
    (r"^/edit_new_objections/\d+(/|$)", "Yangi etiroz tahrirlandi"),
    (r"^/del_new_objections/\d+(/|$)", "Yangi etiroz oʻchirildi"),
    (r"^/add_client_benefits(/|$)", "Yangi foyda qo‘shildi"),
    (r"^/edit_client_benefits/\d+(/|$)", "Yangi etiroz tahrirlandi"),
    (r"^/del_client_benefits/\d+(/|$)", "Yangi etiroz oʻchirildi"),
    (r"^/add_why_buy(/|$)", "Yangi sabab qo‘shildi"),
    (r"^/edit_why_buy/\d+(/|$)", "Yangi sabab tahrirlandi"),
    (r"^/del_why_buy/\d+(/|$)", "Yangi sabab oʻchirildi"),
    (r"^/customer_analysis(/|$)", "Mijozlar tahlili boʻlimi"),
    (r"^/board/instruktsya(/|$)", "Ko’rsatmalar boʻlimi"),
    (r"^/board/instruktsya_list_detail/\d+(/|$)", "Ko’rsatmalar tafsilot boʻlimi"),
    (r"^/board/instruktsya_add(/|$)", "Ko’rsatmalar qo‘shildi"),
    (r"^/board/create_lead(/|$)", "Mijoz qo‘shildi"),
    (r"^/board/change_lead_status(/|$)", "Mijoz xulosa qo‘shildi"),
    (r"^/board/lead_finished(/|$)", "Mijoz yakunlandi"),
    (r"^/board/lead_losed(/|$)", "Mijoz yo‘qotildi"),
    (r"^/board/edit_lead(/|$)", "Mijoz tahrirlandi"),
    (r"^/board/add_pole(/|$)", "Yangi bosqich qo‘shildi"),
    (r"^/board/edit_pole(/|$)", "Yangi bosqich tahrirlandi"),
    (r"^/board/delete_pole(/|$)", "Yangi bosqich oʻchirildi"),
    (r"^/board/shopping/add/\d+(/|$)", "Xarid qilish qo‘shildi"),
    (r"^/board/shopping/edit/\d+(/|$)", "Xarid qilish tahrirlandi"),
    (r"^/board(/|$)", "Mo’ljaldagi potensiallar boʻlimi"),
    (r"^/import_leads_from_excel(/|$)", "Mijozlar excel dan import qilindi"),
]

COMPILED_PATTERNS = [(re.compile(pattern), label) for pattern, label in URL_PATTERNS]

def get_path(path):
    for pattern, label in COMPILED_PATTERNS:
        if pattern.match(path):
            return label
    return 'Nomaʼlum yo‘l'

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            what_did = get_path(request.path)
            if what_did != 'Nomaʼlum yo‘l':
                LastSeen.objects.create(
                    what_did=what_did,
                    account=request.user,
                    company=request.user.company
                )
        return self.get_response(request)
