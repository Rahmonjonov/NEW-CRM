import json
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

import openpyxl
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import AccessMixin
from django.db.models import Sum, Q, Count, F
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from account.functions import checkPhone, sendSmsOneContact, sendSmsOneContact_from_sms_to
from account.models import Plan, Invoice, Card, Company_default_poles, Company, Account, Company_type_choise
from board.models import LeadPoles, LeadAction, CategoryProduct, Region, Lead, District, Task, Product, SMSTemplate, \
    SMS_template_choise, Payment_type, Shopping,Referral, NewComplaints, NewObjections, ClientBenefits, WhyBuy
from board.views import is_B2B, register_lead_send_sms
from goal.models import Goal
from main.models import Calendar, Objections, ObjectionWrite, Script, Debtors, ImportTemplate, Complaint
from django.db.models import Sum
from django.db.models.functions import Coalesce

class LeadMinSerializer(ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name', 'surname', 'price', 'phone']


class SMSTemplateMinSerializer(ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = ['id', 'name', 'type', 'date', 'text']


def pretty_encrypt(string, length, character):
    return character.join(string[i:i + length] for i in range(0, len(string), length))


def ChartLead(request):
    leads = []
    losed = []
    finished = []
    filter_kwargs = {}
    if request.user.is_director:
        filter_kwargs['created_user__company'] = request.user.company
    else:
        filter_kwargs['created_user'] = request.user

    for i in range(1, 13):
        year = datetime.today().year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = str(year) + '-' + str(i) + '-01 00:00:00'
        lte = str(year2) + '-' + str(month2) + '-01 00:00:00'

        count1 = Lead.objects.filter(is_active=True, date__gte=gte, date__lt=lte, status__lte=3, **filter_kwargs).count()
        count2 = Lead.objects.filter(is_active=True, finishedDate__gte=gte, finishedDate__lt=lte, status=4, **filter_kwargs).count()
        count3 = Lead.objects.filter(is_active=True, finishedDate__gte=gte, finishedDate__lt=lte, status=5, **filter_kwargs).count()

        leads.append(count1)
        losed.append(count2)
        finished.append(count3)

    return {
        'leads': leads,
        'losed': losed,
        'finished': finished,
    }


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_or_create_card(request):
    try:
        data = request.data
        company = request.user.company
        card, created = Card.objects.get_or_create(company=company)
        card.name = data['name']
        card.number = data['number']
        card.expire = data['expire']
        card.token = data['token']
        card.active = data['verify'] == 'true'
        card.save()
        if created:
            messages.success(request, f'{card.name} muvaffaqqiyatli qo\'shildi!')
        else:
            messages.success(request, f'{card.name} muvaffaqqiyatli o\'zgartirildi!')

        return Response({"message": "Success"})

    except:
        return Response({"message": "Error"})


@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def edit_company(request):
    try:
        data = request.POST

        company = request.user.company
        company.name = data['name']
        company.phone = data['phone']
        company.manzil = data['manzil']
        company.creator = data['creator']
        company.about = data['about']
        company.type = data['company_type']
        company.save()
        messages.success(request, f'{company.name} muvaffaqqiyatli o\'zgartirildi!')

        return redirect('cabinet')
    except:
        return redirect('cabinet')


@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def edit_product(request, pk):
    if request.method == "GET":
        try:
            product = Product.objects.get(id=pk)
            context = {
                "product": product
            }
            context['company'] = Company.objects.get(id=self.request.user.company.id)
            return render(request, 'edit_product.html', context)
        except:
            return redirect('products')
    else:
        try:
            product = Product.objects.get(id=pk)
            data = request.POST
            product.name = data['name']
            product.price = int(data['price'])
            product.comment = data['comment']
            product.save()
            return redirect('products')
        except:
            return redirect('products')


@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_product(request):
    if request.method == "GET":
        return render(request, 'add_product.html')
    else:
        try:
            data = request.POST
            Product.objects.create(
                company=request.user.company,
                name=data['name'],
                price=int(data['price']),
                comment=data['comment']
            )
            return redirect('products')
        except:
            return redirect('products')


@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_payment_type(request):
    if request.method == "GET":
        return render(request, 'add_payment_type.html')
    else:
        try:
            Payment_type.objects.create(
                company=request.user.company,
                name=request.POST['name'],
            )
            return redirect('products')
        except:
            return redirect('products')


@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def edit_payment_type(request, pk):
    if request.method == "GET":
        try:
            payment_type = Payment_type.objects.get(id=pk)
            context = {
                "payment_type": payment_type
            }
            context['company'] = Company.objects.get(id=self.request.user.company.id)
            return render(request, 'edit_payment_type.html', context)
        except:
            return redirect('products')
    else:
        try:
            payment_type = Payment_type.objects.get(id=pk)
            data = request.POST
            payment_type.name = data['name']
            payment_type.save()
            return redirect('products')
        except:
            return redirect('products')


class Register_class(TemplateView, AccessMixin):
    template_name = 'register.html'

    def post(self, *args, **kwargs):
        try:
            data = self.request.POST

            if Account.objects.filter(username=data['login']).count() == 0:
                if data['password1'] == data['password2']:
                    plan = Plan.objects.filter(is_trial=True).first()
                    company = Company.objects.create(
                        name=data['comp_name'],
                        phone=data['comp_tel'],
                        manzil=data['comp_manzil'],
                        creator=data['comp_creator'],
                        about=data['comp_about'],
                        type=data['company_type'],
                        plan=plan,
                        active=True
                    )

                    user = Account.objects.create(
                        username=data['login'],
                        password=make_password(data['password1']),
                        first_name=data['firstname'],
                        last_name=data['lastname'],
                        company=company,
                        is_director=True
                    )

                    for i in Company_default_poles:
                        LeadPoles.objects.create(
                            name=i[0],
                            status=i[1],
                            company=company
                        )

                    Invoice.objects.create(company=company,
                                           start=datetime.now(),
                                           end=datetime.now() + timedelta(days=14),
                                           plan=company.plan,
                                           summa=company.plan.price,
                                           active=True)
                    messages.success(self.request,
                                     f"{user.username} ro'yxatdan o'tdi!!!\n Sizga 14 kunlik sinov muddasi bilan tizimdan foydalanish huquqi berildi.")
                    login(self.request, user)
                    return redirect('cabinet')
                else:
                    messages.error(self.request, "Parollar bir xil emas!")
            else:
                messages.error(self.request, f"Bu {data['login']} login tanlangan! Boshqa tanlang")

            context = self.get_context_data(*args, **kwargs)
            context['post'] = self.request.POST
            context['company_types'] = Company_type_choise
            return render(self.request, self.template_name, context)
        except:
            return redirect('register')

    def get_context_data(self, *args, **kwargs):
        context = super(Register_class, self).get_context_data(**kwargs)
        context['company_types'] = Company_type_choise
        return context



class Home_new_class(TemplateView, AccessMixin):
    template_name = 'home_new.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Home_new_class, self).get_context_data(**kwargs)
        context['home'] = 'active'
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['users'] = Account.objects.filter(company=self.request.user.company)
        context['lead_poles'] = LeadPoles.objects.filter(company=self.request.user.company)
        mijoz = Lead.objects.filter(is_active=True)
        if self.request.user.is_director:
            mijoz = Lead.objects.filter(is_active=True, created_user__company=self.request.user.company)
        else:
            mijoz = Lead.objects.filter(is_active=True, created_user=self.request.user)
            
            
        context['region'] = Region.objects.all()
        context['district']=District.objects.all()

        district  = self.request.GET.get('district')

        emotsiya = self.request.GET.get('emotsiya')

        if emotsiya:
            for i in (LeadAction.objects.select_related('lead__created_user__company', 'lead').
                    filter(emotsiya=emotsiya, lead__created_user__company=self.request.user.company)
                    .values('lead', 'lead__created_user__company').distinct()):
                mijoz = mijoz.filter(id=i['lead'])

        if district:
            mijoz = mijoz.filter(is_active=True, district_id=district)
            district_obj = District.objects.get(id=district)
            context['district'] = District.objects.filter(region=district_obj.region)
        


        context['lead'] = mijoz.filter(status__gte=0, status__lte=3).count()
        context['lead0'] = mijoz.filter(status=4).count()
        context['lead1'] = mijoz.filter(status=5).count()
        context['chart'] = ChartLead(self.request)
        
        context['umumiy_leds_count'] = mijoz.filter(is_active=True, status=5, created_user__is_influencer=False).count()
        context['umumiy_leads_summa'] = mijoz.filter(is_active=True, status=5, created_user__is_influencer=False).aggregate(all=Coalesce(Sum('price'), 0))['all']

        context['umumiy_leds_count_influser'] = mijoz.filter(is_active=True, status=5,created_user__is_influencer=True).count()
        context['umumiy_leads_summa_influser'] = mijoz.filter(is_active=True, status=5,created_user__is_influencer=True).aggregate(all=Coalesce(Sum('price'), 0))['all']

        debt = mijoz.filter(debt__gt=0)

        context['debtor'] = debt.count()
        context['debtor_sum'] = debt.aggregate(Sum('debt'))['debt__sum']

        context['debtor_influser'] = debt.filter(created_user__is_influencer=True).count()
        context['debtor_sum_influser'] = debt.filter(created_user__is_influencer=True).aggregate(Sum('debt'))['debt__sum']
        
        # begin goal
        if self.request.user.is_director:
            accounts = Account.objects.filter(company=self.request.user.company)
            list = []
            for a in accounts:
                lc = mijoz.filter(is_active=True, created_user=a).count()
                try:
                    goal = Goal.objects.get(user=a, oy=datetime.today().month, yil=datetime.today().year)
                    actions = Lead.objects.filter(finishedDate__month=datetime.today().month, finishedDate__year=datetime.today().year, created_user=a)
                    act_sum = sum([i.finishedPrice for i in actions])
                    t = {
                        'name': a.first_name,
                        'surname': a.last_name,
                        'foiz': int((lc / (goal.mijoz_soni if goal.mijoz_soni else 0)) * 100),
                        'foiz_summa': int(100 / (goal.savdo if goal.savdo else 1) * (act_sum if act_sum != 0 else 1)),
                        'summa': act_sum,
                        'plan_summa': goal.savdo,
                    }
                except:
                    t = {
                        'name': a.first_name,
                        'surname': a.last_name,
                        'foiz': 0,
                        'foiz_summa': 0,
                        'summa': 0,
                        'plan_summa': 0,
                    }
                list.append(t)
            context['acc'] = list
        else:
            lc = mijoz.filter(is_active=True, created_user=self.request.user).count()
            try:
                goal = Goal.objects.get(user=self.request.user, oy=datetime.today().month, yil=datetime.today().year)
                t = {
                    'name': self.request.user.first_name,
                    'surname': self.request.user.last_name,
                    'foiz': int((lc / goal.mijoz_soni) * 100)
                }
            except:
                t = {
                    'name': self.request.user.first_name,
                    'surname': self.request.user.last_name,
                    'foiz': 0
                }
            context['a'] = t
        # end goal

        context['leads_count'] = mijoz.exclude(status=5).count()
        context['leads_summa'] = mijoz.exclude(status=5).aggregate(Sum('price'))['price__sum']
        
        context['lead_influser'] = mijoz.filter(status__gte=0, status__lte=3, created_user__is_influencer=True).exclude(status=5).count()
        context['leads_summa_influser'] = mijoz.filter(created_user__is_influencer=True).exclude(status=5).aggregate(Sum('price'))['price__sum']

        context['active_leads_count'] = mijoz.filter(status__lt=4).count()
        context['active_leads_summa'] = mijoz.filter(status__lt=4).aggregate(Sum('price'))['price__sum']

        context['active_leads_count_influser'] = mijoz.filter(status__lt=4, created_user__is_influencer=True).count()
        context['active_leads_summa_influser'] = mijoz.filter(status__lt=4, created_user__is_influencer=True).aggregate(Sum('price'))['price__sum']


        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CalenApp(TemplateView, AccessMixin):
    template_name = 'apps-calendar.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CalenApp, self).get_context_data(**kwargs)
        context['appcalendar'] = 'active'
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['users'] = Lead.objects.filter(is_active=True, created_user__company=self.request.user.company)

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class Product_list_class(TemplateView, AccessMixin):
    template_name = 'product_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Product_list_class, self).get_context_data(**kwargs)
        context['product_page'] = "active"
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['products'] = Product.objects.filter(company=self.request.user.company)
        context['payment_types'] = Payment_type.objects.filter(company=self.request.user.company)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


def GetCalendar(request):
    if request.user.is_director:
        calens = Calendar.objects.filter(created_user__company=request.user.company)
    else:
        calens = Calendar.objects.filter(created_user=request.user)
    c = []
    for i in calens.filter(user__isnull=False):
        j = {
            'id': i.id,
            'color': i.color,
            'event': i.event,
            'date': i.date,
            'user': i.user.full_name,
        }
        c.append(j)
    dt = {
        "calendars": c,
    }
    return JsonResponse(dt)


def AddEvent(request):
    user = request.user
    if request.method == "POST":
        r = request.POST
        event = r['event']
        date = r['date']
        color = r['color']
        Calendar.objects.create(event=event, date=date, color=color, created_user=user)
    return redirect('calendar1')


class Etiroz(TemplateView, AccessMixin):
    template_name = 'etiroz.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Etiroz, self).get_context_data(**kwargs)
        context['etiroz'] = 'active'
        context['objections'] = Objections.objects.filter(create_user__company=self.request.user.company)
        context['objectionwrite'] = ObjectionWrite.objects.filter(create_user__company=self.request.user.company)
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        try:
            context['ckeditor'] = Script.objects.filter(create_user__company=self.request.user.company).first()
        except:
            context['ckeditor'] = None

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)

from django.db.models import Q

class Target(TemplateView, AccessMixin):
    template_name = 'target.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Target, self).get_context_data(**kwargs)
        context['target'] = 'active'
        lead = Lead.objects.filter(is_active=True,created_user__company=self.request.user.company)
        district = self.request.GET.get('district')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        emotsiya = self.request.GET.get('emotsiya')
        context['today'] = datetime.today().date()
        context['first_day_of_month'] = datetime.today().date().replace(day=1)
        context['region'] = Region.objects.all()
        context['district'] = District.objects.all()

        if district:
            lead = lead.filter(district_id=district)
            district_obj = District.objects.get(id=district)
            context['district'] = District.objects.filter(region=district_obj.region)
        
        if start_date and end_date:
            lead = lead.filter(date__date__gte=start_date, date__date__lte=end_date)
        else:
            lead = lead.filter(date__date__gte=context['first_day_of_month'])
        
        if emotsiya:
                for i in LeadAction.objects.select_related('lead__created_user__company', 'lead').filter(emotsiya=emotsiya,
                 lead__created_user__company=self.request.user.company).values('lead', 'lead__created_user__company').distinct():
                    lead = lead.filter(id=i['lead'])

        if self.request.user.is_director:
            context['company'] = Company.objects.get(id=self.request.user.company.id)
            context['lead'] = lead.filter(status__gte=1, status__lte=4)
            context['mijoz'] = lead.filter(status=5)
            context['lead0'] = lead.filter(status=0)
            context['promouter'] = lead.filter(status=6)
            context['lead_count'] = lead.filter(status__gte=1, status__lte=4).count()
            context['mijoz_count'] = lead.filter(status=5).count()
            context['lead0_count'] = lead.filter(status=0).count()
            context['promouter_count'] = lead.filter(status=6).count()

        else:
            context['lead'] = lead.filter(status__gte=1, status__lte=4)
            context['mijoz'] = lead.filter(is_active=True, status=5, created_user=self.request.user)
            context['lead0'] = lead.filter(is_active=True, status=0, created_user=self.request.user)
            context['promouter'] = lead.filter(is_active=True, status=6, created_user=self.request.user)
            context['lead_count'] = lead.filter(is_active=True, status__gte=1, status__lte=4,created_user=self.request.user).count()
            context['mijoz_count'] = lead.filter(is_active=True, status=5, created_user=self.request.user).count()
            context['lead0_count'] = lead.filter(is_active=True, status=0, created_user=self.request.user).count()
            context['promouter_count'] = lead.filter(is_active=True, status=6,created_user=self.request.user).count()

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class Clients(TemplateView, AccessMixin):
    template_name = 'clients.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Clients, self).get_context_data(**kwargs)
        context['client'] = 'active'

        region = self.request.GET.get('region')
        district = self.request.GET.get('district')
        users = self.request.GET.get('users')
        date_range = self.request.GET.get('date')

        context['company'] = Company.objects.get(id=self.request.user.company.id)
        leads = Lead.objects.all()
        if self.request.user.is_director:
            leads = leads.filter(is_active=True, created_user__company=self.request.user.company)
        else:
            leads = leads.filter(is_active=True, created_user=self.request.user)

        if district:
            leads = leads.filter(district__id=district)

        if users:
            leads = leads.filter(created_user__id=users)

        if date_range:
            start_str, end_str = date_range.split(' - ')
            start_date = datetime.strptime(start_str, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_str, '%m/%d/%Y').date()
            
            leads = leads.filter(date__date__range=(start_date, end_date))
            
        context['clients']  = leads
        context['template_excel'] = ImportTemplate.objects.first()
        context['region'] = Region.objects.all()
        context['district'] = District.objects.all()
        context['users'] = Account.objects.filter(company=self.request.user.company)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class Setting(TemplateView, AccessMixin):
    template_name = 'setting.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Setting, self).get_context_data(**kwargs)
        context['setting'] = 'active'
        context['token'] = self.request.user.company.tg_token
        context['users'] = Account.objects.filter(company=self.request.user.company)
        context['referral'] = Referral.objects.filter(company=self.request.user.company)
        context['company'] = self.request.user.company
        context['leads'] = LeadPoles.objects.filter(company=self.request.user.company)
        
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)

def add_referall(request):
    Referral.objects.create(name=request.POST.get('name'), company=request.user.company)
    return redirect(request.META['HTTP_REFERER'])

def edit_referall(request, id):
    Referral.objects.filter(id=id, company=request.user.company).update(name=request.POST.get('name'))
    return redirect(request.META['HTTP_REFERER'])

def del_referall(request, id):
    Referral.objects.filter(id=id, company=request.user.company).update(is_activate=False)
    return redirect(request.META['HTTP_REFERER'])

def change_company_informations(request):
    r = request.POST.get
    name = r('name')
    phone = r('phone')
    manzil = r('manzil')
    type = r('type')
    info = r('info')
    logo = request.FILES.get('logo')
    
    company = request.user.company
    company.name = name
    company.phone = phone
    company.manzil = manzil
    company.type = type
    company.info = info
    if logo:
        company.logo = logo
    company.save()

    return redirect(request.META['HTTP_REFERER'])
@login_required
def importLead(request):
    if request.method == 'GET':
        return render(request, 'importLead.html')
    else:
        try:
            excel_file = request.FILES['leads']
            wb = openpyxl.load_workbook(excel_file)
            worksheet = wb.active
            count = 0
            user = request.user

            for row in worksheet.iter_rows():
                if count == 0:
                    count += 1
                else:
                    name = row[0].value
                    surname = row[1].value
                    price = int(row[2].value)
                    company = row[3].value
                    companyAddress = row[4].value
                    phone = row[5].value
                    lead = Lead.objects.create(
                        name=name,
                        status=5,
                        surname=surname,
                        price=price,
                        company=company,
                        companyAddress=companyAddress,
                        phone=phone,
                        created_user=user
                    )

                    LeadAction.objects.create(lead=lead, changer=user)
            messages.success(request, "Mijozlar muvaffaqqiyatli yuklandi")
        except:
            messages.error(request, "Yuklashda xatolik")
        return redirect('clients')


# begin smstemplate

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def sms_template_status_change(request):
    try:
        pk = int(request.GET.get("pk"))
        val = int(request.GET.get("val"))
        obj = SMSTemplate.objects.get(id=pk)
        newV = True
        if val == 0:
            newV = False
        obj.active = newV
        obj.save()
        return Response({"status": 200})
    except:
        return Response({"status": 500})


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def search_lead(request):
    try:
        text = request.GET.get('text')
        leads = Lead.objects.filter(is_active=True, 
            created_user__company=request.user.company
        ).filter(
            Q(name__icontains=text) |
            Q(surname__icontains=text) |
            Q(company__icontains=text) |
            Q(phone__icontains=text)
        )[:30]
        return Response(LeadMinSerializer(leads, many=True).data)
    except:
        return Response([])


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def filter_lead(request):
    try:
        poles = json.loads(request.data.get('poles'))
        status = json.loads(request.data.get('status'))

        leads = Lead.objects \
            .filter(created_user__company=request.user.company) \
            .filter(Q(status__in=status) |
                    (Q(status=0) & Q(pole_id__in=poles)))
        # status=0 bolishi kerak lead bordda bo'lishi uchun

        return Response(LeadMinSerializer(leads, many=True).data)
    except:
        return Response({"message": "error"}, status=500)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def save_sms_template(request):
    try:
        name = request.data['name']
        text = request.data['smstext']
        smstype = request.data['sms_type']
        date = request.data['date']
        leads = json.loads(request.data['leads'])
        if request.data.get('pk'):
            pk = int(request.data.get('pk'))
            template = SMSTemplate.objects.get(id=pk)
            template.name = name
            template.text = text
            template.type = smstype
            template.save()
        else:
            template = SMSTemplate.objects. \
                create(company=request.user.company,
                       name=name, text=text,
                       type=smstype,
                       active=True
                       )
        if smstype == "Bayram va boshqalar":
            template.leads.clear()
            template.leads.set(leads)
            template.date = date
            template.save()
        return Response({})
    except:
        return Response({}, status=500)


@login_required()
def delete_sms_template(request, pk):
    try:
        SMSTemplate.objects.get(company=request.user.company, id=pk).delete()
    except:
        pass
    return redirect("sms")


# end smstemplate


class Debt(TemplateView, AccessMixin):
    template_name = 'debt.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Debt, self).get_context_data(**kwargs)
        context['debt'] = 'active'
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['debtors'] = Lead.objects.filter(is_active=True, debt__gt=0, created_user__company=self.request.user.company)

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class Sms(TemplateView, AccessMixin):
    template_name = 'sms.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Sms, self).get_context_data(**kwargs)
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['lead_count'] = Lead.objects.filter(is_active=True, created_user__company=self.request.user.company).count()
        context['sms'] = 'active'
        context['illness'] = CategoryProduct.objects.all()
        context['lead_status_types'] = [item for item in Lead.status_types if item[0] > 0]
        context['lead_poles'] = LeadPoles.objects.filter(company=self.request.user.company)
        context['leads'] = Lead.objects.filter(is_active=True, created_user__company=self.request.user.company)
        context['sms_templates'] = SMSTemplate.objects.filter(company=self.request.user.company)

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class NewSMSTemplate_class(TemplateView, AccessMixin):
    template_name = 'newSmsTemplate.html'

    def get_context_data(self, *args, **kwargs):
        context = super(NewSMSTemplate_class, self).get_context_data(**kwargs)
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['sms_templates'] = SMS_template_choise
        context['lead_status_types'] = [item for item in Lead.status_types if item[0] > 0]
        context['lead_poles'] = LeadPoles.objects.filter(company=self.request.user.company)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class EditSMSTemplate_class(TemplateView, AccessMixin):
    template_name = 'editSMSTemplate.html'
    smstemplate = None

    def get_context_data(self, *args, **kwargs):
        context = super(EditSMSTemplate_class, self).get_context_data(**kwargs)
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['sms_templates'] = SMS_template_choise
        context['lead_status_types'] = [item for item in Lead.status_types if item[0] > 0]
        context['lead_poles'] = LeadPoles.objects.filter(company=self.request.user.company)
        context['current_template'] = self.smstemplate
        context['current_leads_dumps'] = json.dumps(LeadMinSerializer(self.smstemplate.leads.all(), many=True).data)
        context['current_template_dumps'] = json.dumps(SMSTemplateMinSerializer(self.smstemplate).data)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        pk = kwargs['pk']
        try:
            self.smstemplate = SMSTemplate.objects.get(company=self.request.user.company, id=pk)
        except SMSTemplate.DoesNotExist:
            return redirect("sms")
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class Cabinet(TemplateView, AccessMixin):
    template_name = 'companyCabinet.html'

    def post(self, *args, **kwargs):
        new_plan = int(self.request.POST['new_plan'])
        company = self.request.user.company
        company.plan_id = new_plan
        company.save()
        messages.success(self.request,
                         mark_safe(f'{company.name} tarifi {company.plan.name} ga o\'zgartirildi! Joriy tarifni amal '
                                   f'qilishi yakunlandan so\'ng <span style="color:#000">{company.plan.name}</span> tarif ishga tushadi.'))
        return redirect('cabinet')

    def get_context_data(self, *args, **kwargs):
        context = super(Cabinet, self).get_context_data(**kwargs)
        context['plans'] = Plan.objects.all()
        invoices = Invoice.objects.filter(company=self.request.user.company).order_by('-id')
        try:
            card = Card.objects.get(company=self.request.user.company)
        except Card.DoesNotExist:
            card = None
        context['card'] = card
        if card:
            context['number'] = pretty_encrypt(card.number, 4, ' ')
            context['expire'] = pretty_encrypt(card.expire, 2, '/')

        context['invoices'] = invoices
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['active_invoice'] = invoices.filter(active=True).first()
        context['company_types'] = Company_type_choise
        try:
            context['kam_summa'] = abs(self.request.user.company.balance - self.request.user.company.plan.price)

        except:
            pass
        context['kabinet'] = "active"
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CardAdd_or_edit(TemplateView, AccessMixin):
    template_name = 'add_card.html'

    def post(self, *args, **kwargs):
        new_plan = int(self.request.POST['new_plan'])
        company = self.request.user.company
        company.plan_id = new_plan
        company.save()
        messages.success(self.request,
                         mark_safe(f'{company.name} tarifi {company.plan.name} ga o\'zgartirildi! Joriy tarifni amal '
                                   f'qilishi yakunlandan so\'ng <span style="color:#000">{company.plan.name}</span> tarif ishga tushadi.'))
        return redirect('cabinet')

    def get_context_data(self, *args, **kwargs):
        context = super(CardAdd_or_edit, self).get_context_data(**kwargs)
        try:
            card = Card.objects.get(company=self.request.user.company)
        except Card.DoesNotExist:
            card = None
        if card is not None:
            context['card'] = card
        context['merchant_id'] = settings.PAYCOM_MERCHANT_ID
        context['paycom_is_test'] = settings.PAYCOM_IS_TEST
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def SmsGateway(request):
    if request.method == 'POST':
        sms = request.POST['sms']
        company = request.user.company
        status_codes = request.POST.get('user_type')
        pole_list = request.POST.get('pole_type')
        if status_codes == "":
            status = []
        else:
            status = json.loads(status_codes)
        if pole_list == "":
            poles = []
        else:
            poles = json.loads(pole_list)

        leads_id = request.POST.getlist('leads')
        leads = Lead.objects.filter(is_active=True, id__in=leads_id)
        success_send_count = 0
        error_send_count = 0
        Leads = Lead.objects \
            .filter(created_user__company=company) \
            .filter(Q(status__in=status) | (Q(status=0) & Q(
            pole_id__in=poles)))

        if company.sms_activated:
            for lead in leads:
                can, phone = checkPhone(lead.phone)
                if can:
                    result = sendSmsOneContact(company, phone, sms)
                    print(result)
                    print(company)
                    print(phone)
                    print(sms)
                    if result.status_code == 200:
                        success_send_count += 1
                    else:
                        error_send_count += 1

                else:
                    error_send_count += 1

            # for lead in leads:

            #     can, phone = checkPhone(lead.phone)
            #     if can:
            #         result = sendSmsOneContact(company, phone, sms)
            #         if result.status_code == 200:
            #             success_send_count += 1
            #         else:
            #             error_send_count += 1
            #     else:
            #         error_send_count += 1

        elif company.smsto_activated:
            for lead in Leads:
                result = sendSmsOneContact_from_sms_to(company, lead.phone, sms)
                if result.status_code == 200:
                    success_send_count += 1
                else:
                    error_send_count += 1

            for lead in leads:
                result = sendSmsOneContact_from_sms_to(company, lead.phone, sms)
                if result.status_code == 200:
                    success_send_count += 1
                else:
                    error_send_count += 1

        if success_send_count > 0:
            messages.success(request, f"{success_send_count} ta sms jo'natildi!")
        if error_send_count > 0:
            messages.error(request, f"{error_send_count} ta sms jo'natilmadi!")
    return redirect('sms')


class Hodim(TemplateView, AccessMixin):
    template_name = 'hodim.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_director:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(Hodim, self).get_context_data(**kwargs)
        context['hodim'] = 'active'
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        context['users'] = Account.objects.filter(company=self.request.user.company)

        return context


def DeleteHodim(request):
    h_id = request.GET.get('id')
    Account.objects.get(id=h_id).delete()

    return redirect('hodim')


def ObjectWrite(request):
    if request.method == "POST":
        obj = request.POST['objection']
        sol = request.POST['solution']

        ObjectionWrite.objects.create(objection=obj, solution=sol, create_user=request.user)

        return redirect('etiroz')
    else:
        return redirect('etiroz')


def Obj(request):
    if request.method == "POST":
        obj = request.POST['objection']
        sol = request.POST['solution']

        Objections.objects.create(objection=obj, solution=sol, create_user=request.user)

        return redirect('etiroz')
    else:
        return redirect('etiroz')


def CalenEdit(request):
    today = datetime.now()
    c = Calendar.objects.filter(date__gte=today).order_by('date')

    context = {
        'calens': c,
    }
    context['company'] = Company.objects.get(id=request.user.company.id)
    return render(request, 'calenedit.html', context)


def CalenEditForm(request):
    context = {}
    if request.method == "GET":
        pk = request.GET.get('id')
        c = Calendar.objects.get(id=pk)

        context = {
            'calen': c
        }
    context['company'] = Company.objects.get(id=self.request.user.company.id)
    return render(request, 'caleneditform.html', context)


def CalenDel(request):
    if request.method == "GET":
        pk = request.GET.get('id')
        Calendar.objects.get(id=pk).delete()
    return redirect('calenedit')


def Delete(request):
    if request.method == "GET":
        pk = request.GET.get('id')
        t = request.GET.get('t')
        if t == '1':
            o = Objections.objects.get(id=pk)
            o.delete()
        elif t == '2':
            o = ObjectionWrite.objects.get(id=pk)
            o.delete()
        return redirect('etiroz')
    else:
        return redirect('etiroz')


def SaveEditCalen(request):
    if request.method == "POST":
        r = request.POST
        pk = r['id']
        event = r['event']
        date = r['date']
        color = r['color']

        c = Calendar.objects.get(id=pk)
        c.event = event
        c.color = color
        c.date = date
        c.save()

    return redirect('calenedit')


def AddHodim(request):
    if request.method == "POST":
        r = request.POST
        fam = r['fam']
        ism = r['ism']
        username = r['username']
        password = r['password']
        is_influencer = r.get('is_influencer', 0)
        try:
            current_count = Account.objects.filter(company=request.user.company).count()
            if request.user.company.plan.max_worker_count <= current_count:
                return redirect('hodim')
        except:
            pass
        try:
            acc = Account.objects.create(username=username, password=make_password(password), first_name=ism, last_name=fam,
                                   company=request.user.company,)
            if int(is_influencer) == 1:
                acc.is_director = True
                acc.save()

            elif int(is_influencer) == 2:
                acc.is_influencer = True
                acc.save()
        except:
            messages.error(request, "Bu username mavjud")
        return redirect('hodim')


def Edito(request):
    if request.method == "GET":
        pk = request.GET.get('id')
        t = request.GET.get('t')
        try:
            ck = Script.objects.first()
        except:
            ck = None
        if t == '1':
            o = Objections.objects.get(id=pk)
            context = {
                'objections': Objections.objects.filter(create_user__company=request.user.company),
                'objectionwrite': ObjectionWrite.objects.filter(create_user__company=request.user.company),
                'obj': o,
                'ckeditor': ck,
                't': 1
            }
            context['company'] = Company.objects.get(id=request.user.company.id)
            return render(request, 'etiroz.html', context)
        elif t == '2':
            o = ObjectionWrite.objects.get(id=pk)
            context = {
                'objections': Objections.objects.filter(create_user__company=request.user.company),
                'objectionwrite': ObjectionWrite.objects.filter(create_user__company=request.user.company),
                'obj': o,
                'ckeditor': ck,
                't': 2
            }
            context['company'] = Company.objects.get(id=request.user.company.id)
            return render(request, 'etiroz.html', context)
    else:
        return redirect('etiroz')


def Save(request):
    if request.method == "POST":
        o = request.POST['objection']
        s = request.POST['solution']
        id = request.POST['id']
        t = request.POST['t']
        if t == '1':
            obj = Objections.objects.get(id=id)
            obj.objection = o
            obj.solution = s
            obj.save()
        elif t == '2':
            obj = ObjectionWrite.objects.get(id=id)
            obj.objection = o
            obj.solution = s
            obj.save()

    return redirect('etiroz')


def Ckeditor(request):
    if request.method == 'POST':
        ck = request.POST['editor1']
        try:
            s = Script.objects.filter(create_user__company=request.user.company).first()
            s.text = ck
            s.save()
        except:
            Script.objects.create(text=ck, create_user=request.user)

        return redirect('etiroz')
    else:
        return redirect('etiroz')


def Edit(request):
    if not request.user.company.active:
        return redirect('cabinet')

    if request.method == 'GET':
        id = request.GET.get('id')
        lead = Lead.objects.get(id=id)
        if lead.step1 is None:
            step = 1
        elif lead.step2 is None:
            step = 2
        elif lead.step3 is None:
            step = 3
        elif lead.step4 is None:
            step = 4
        else:
            step = 5
        try:
            user = {
                'id': lead.id,
                'first_name': lead.name,
                'last_name': lead.surname,
                'birthday': lead.birthday,
                'phone': lead.phone,
                'email': lead.email,
                'region': lead.district.region.name,
                'district': lead.district.name,
                'degree': lead.degr[lead.degree - 1][1],
                'abcxyz': lead.abcxyz,
                'step1': lead.step1,
                'step2': lead.step2,
                'step3': lead.step3,
                'step4': lead.step4,
                'step5': lead.step5,
                'note': lead.note,
                'tg_id': lead.tg_id,
            }
        except:
            user = {
                'id': lead.id,
                'first_name': lead.name,
                'last_name': lead.surname,
                'birthday': lead.birthday,
                'phone': lead.phone,
                'email': lead.email,
                'degree': lead.degr[lead.degree - 1][1],
                'abcxyz': lead.abcxyz,
                'step1': lead.step1,
                'step2': lead.step2,
                'step3': lead.step3,
                'step4': lead.step4,
                'step5': lead.step5,
                'note': lead.note,
                'tg_id': lead.tg_id,
            }

        context = {
            'status': Lead.objects.filter(id=id),
            'lead_poles': LeadPoles.objects.filter(company=request.user.company),
            'userr': user,
            'step': step,
            'lead': lead,
            'region': Region.objects.all(),
            'district': District.objects.all(),
            'notes': LeadAction.objects.filter(lead_id=id).order_by('-ping', '-date'),
            'products': Product.objects.filter(company=request.user.company),
            'payment_types': Payment_type.objects.filter(company=request.user.company),
            'shoppings': Shopping.objects.filter(lead=lead),
            'account':Account.objects.filter(company=request.user.company),
            'referral' : Referral.objects.filter(company=request.user.company),
            'complaints': NewComplaints.objects.filter(lead=lead),
            'new_objections':NewObjections.objects.filter(lead=lead),
            'client_benefits':ClientBenefits.objects.filter(lead=lead),
            'why_buy':WhyBuy.objects.filter(lead=lead),
            
        }
        context['company'] = Company.objects.get(id=request.user.company.id)
        return render(request, 'edit.html', context)

    elif request.method == 'POST':
        id = int(request.POST['id'])
        u = Lead.objects.get(id=id)
        try:
            surname = request.POST['surname']
            u.surname = surname
        except:
            pass
        try:
            phone = request.POST['phone']
            u.phone = phone
        except:
            pass
        try:
            email = request.POST['email']
            u.email = email
        except:
            pass
        try:
            region = request.POST['region']
            u.region = region
        except:
            pass
        try:
            district = request.POST['district']
            u.district = district
        except:
            pass
        try:
            birthday = request.POST['birthday']
            u.birthday = birthday
        except:
            pass
        try:
            district = request.POST['district']
            u.district_id = district
        except:
            pass
        try:
            abc = request.POST['abc']
            u.abcxyz = abc
        except:
            pass
        try:
            status = request.POST['status']
            u.status = status
        except:
            pass
        try:
            notes = request.POST['notes']
            u.note = notes
        except:
            pass
        try:
            u.join_from = request.POST['join_from']
        except:
            pass
        try:
            u.phone2 = request.POST['phone2']
        except:
            pass
        try:
            u.telegram_phone_number = request.POST['telegram_phone_number']
        except:
            pass
        try:
            u.referral_id = request.POST['referral']
        except:
            pass
        try:
            u.pole_id = request.POST['pole']
        except:
            pass
        u.save()

        return redirect('target')


@csrf_exempt
def notes_ping(request, id):
    ping = request.POST.get('ping')
    print(ping)
    notes = LeadAction.objects.get(id=id)
    notes.ping = True if ping == 'True' else False
    notes.save()
    return JsonResponse({"response": 'succes'})


import openai


from openai import OpenAI  

client = OpenAI(api_key="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")

@csrf_exempt
def chat_with_gpt(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "Siz foydalanuvchiga yordam beruvchi ChatGPT assistant siz."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = chat_response.choices[0].message.content
        return JsonResponse({"response": reply})
    return JsonResponse({"error": "Only POST method allowed"}, status=405)


def add_task_with_lead(request, id):
    lead = LeadAction.objects.get(id=id)
    lead_status = request.POST.get('type_task')
    name = request.POST.get('name')
    customer = request.POST.get('customer')
    datetime = request.POST.get('datetime')
    Task.objects.create(
        lead_action=lead,
        lead_status=lead_status,
        name=name,
        customer_id=customer,
        created_user=request.user,
        note=lead.note,
        lead_date_time=datetime
    )
    return redirect(request.META['HTTP_REFERER'])


def AddUser(request):
    if not request.user.company.active:
        return redirect('cabinet')
    u = request.user
    if request.method == "POST":
        r = request.POST
        ism = r['ism']
        fam = r['fam']
        phone = r['tel']
        phone2 = r['tel2']
        birthday = r['birth']
        dis = r['district']
        abc = r['abc']
        price = r['price']
        join_from = r['join_from']
        try:
            Lead.objects.get(phone=phone, created_user__company=request.user.company)
            messages.add_message(request, messages.ERROR, f"{ism} avval ro'yxatdan o'tgan")
            return redirect('adduser')
        except:
            u = Lead.objects.create(name=ism,
                                    surname=fam,
                                    phone=phone,
                                    phone2=phone2,
                                    birthday=birthday,
                                    abcxyz=abc,
                                    district_id=dis,
                                    created_user=u,
                                    price=price,
                                    join_from=join_from,
                                    pole_id=int(r['lead_pole']))
            if is_B2B(request):
                u.company = r['com']
                u.companyAddress = r['comadd']
                u.save()
            u.save()
            register_lead_send_sms(u)
            messages.add_message(request, messages.SUCCESS, f"{phone} Qo'shildi")
        return redirect('target')
    else:
        context = {
            'region': Region.objects.all(),
            'lead_poles': LeadPoles.objects.filter(company=request.user.company),
            'district': District.objects.all(),
            'products': Product.objects.filter(company=request.user.company),
            'payment_types': Payment_type.objects.filter(company=request.user.company)
        }
        context['company'] = Company.objects.get(id=request.user.company.id)
        return render(request, 'adduser.html', context)


def Up(request):
    if not request.user.company.active:
        return redirect('cabinet')
    if request.method == 'GET':
        id = int(request.GET.get('id'))
        s = int(request.GET.get('s'))
        u = Lead.objects.get(id=id)
        u.status = s
        u.date = datetime.now()
        u.save()
    return redirect('target')

def delete_lead(request):
    if not request.user.company.active:
        return redirect('cabinet')
    if request.method == 'GET':
        id = int(request.GET.get('id'))
        lead = Lead.objects.get(id=id)
        lead.is_active = False
        lead.save()
        return redirect('target')


def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Login yoki Parol noto`g`ri kiritildi!')
            return redirect('login')
    else:
        return render(request, 'login.html')


def Logout(request):
    logout(request)
    messages.success(request, "Tizimdan chiqish muvaffaqiyatli yakunlandi!")
    return redirect('login')


def customhandler404(request, exception, template_name='404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def AddNotes(request):
    if not request.user.company.active:
        return redirect('cabinet')
    u = request.user
    if request.method == "POST":
        note = request.POST['note']
        id = request.POST['id']
        color = request.POST['color']
        emotsiya = request.POST.get('emotsiya')
        LeadAction.objects.create(note=note, lead_id=id, color=color, changer=u, emotsiya=emotsiya)
        url = '/edit/?id=' + str(id)
        return redirect(url)


def DebtHistory(request):
    if not request.user.company.active:
        return redirect('cabinet')
    if request.method == "GET":
        id = request.GET.get('id')

        ol = Debtors.objects.filter(user_id=id, debt=1, user__created_user__company=request.user.company).order_by(
            '-id')
        ber = Debtors.objects.filter(user_id=id, debt=0, user__created_user__company=request.user.company).order_by(
            '-id')

        context = {
            'olingan': ol,
            'berilgan': ber,
            'usr': id,
        }
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return render(request, 'debthistory.html', context)


def AddDebt(request):
    if not request.user.company.active:
        return redirect('cabinet')
    if request.method == "POST":
        r = request.POST
        u_id = r['u_id']
        debt = r['debt']
        summa = int(r['summa'])
        user = Lead.objects.get(id=u_id)
        if debt == '1':
            user.debt += summa
            user.save()
        else:
            user.debt -= summa
            user.save()
        Debtors.objects.create(user_id=u_id, summa=summa, debt=debt, create_user=request.user)
        url = '/debthistory/?id=' + u_id
        return redirect(url)


def AddDebtor(request):
    if request.method == "POST":
        r = request.POST
        u_id = r['debtor']
        debt = int(r['debt'])
        user = Lead.objects.get(id=u_id)
        user.debt += debt
        user.save()
        Debtors.objects.create(user_id=u_id, summa=debt, debt=1, create_user=request.user)

        return redirect('debt')
    else:
        context = {
            'debtors': Lead.objects.filter(is_active=True, debt=0, created_user__company=request.user.company),
            'method': 'get',
        }
        context['company'] = Company.objects.get(id=request.user.company.id)
        return render(request, 'adddebtor.html', context)


def EditSpin(request):
    if request.method == "POST":
        r = request.POST
        u_id = r['u_id']
        step = r['step']
        st = r['st']
        url = '/edit/?id=' + u_id
        print(u_id, 'hhhhhhh')
        print(step, ';;;;;;;;;;;')
        print(st, '!!!!!!!!!!!')
        user = Lead.objects.get(id=u_id)
        if st == '1':
            user.step1 = step
        elif st == '2':
            user.step2 = step
        elif st == '3':
            user.step3 = step
        elif st == '4':
            user.step4 = step
        elif st == '5':
            user.step5 = step
        user.save()
        return redirect(url)
    else:
        return redirect('target')


def PostEvent(request):
    data = json.loads(request.body)
    user = data['user']
    title = data['title']
    time = data['start']
    className = data['className']
    Calendar.objects.create(user_id=user, event=title, date=time, color=className, created_user=request.user)
    return JsonResponse({})


def DelEvent(request):
    id = request.GET.get('id')
    Calendar.objects.get(id=id).delete()
    return JsonResponse({})


def EditEvent(request):
    data = json.loads(request.body)
    id = data['id']
    user = data['user']
    title = data['title']
    time = data['start']
    className = data['className']

    c = Calendar.objects.get(id=id)
    c.user_id = user
    c.event = title
    c.date = time
    c.color = className
    c.save()

    return JsonResponse({})


@login_required
def main_statistika(request):
    try:
        # types = ((1, "Bugunlik"), (2, "Haftalik"), (3, "Oylik"), (4, "Sana range"))
        user_pk = int(request.GET.get('pk'))
        type = int(request.GET.get('type'))

        sana = datetime.today().date()
        if type == 1:
            sana1 = datetime(sana.year, sana.month, sana.day)
            sana2 = datetime.fromordinal(sana.toordinal() + 1)
        elif type == 2:
            sana1 = datetime.fromordinal(sana.toordinal() - 6)
            sana2 = datetime.fromordinal(sana.toordinal() + 1)
        elif type == 3:
            sana1 = datetime.fromordinal(sana.toordinal() - 29)
            sana2 = datetime.fromordinal(sana.toordinal() + 1)
        elif type == 4:
            date1 = request.GET.get('sana1')
            date2 = request.GET.get('sana2')
            dt1 = date1.split('/')
            dt2 = date2.split('/')
            sana1 = datetime(int(dt1[2]), int(dt1[0]), int(dt1[1]))
            sana2 = datetime(int(dt2[2]), int(dt2[0]), int(dt2[1]))
        else:
            return Response({"message": "type error"})
        user = request.user
        d_f_kwargs = {
            "date__gte": sana1,
            "date__lt": sana2,
        }
        users_data = []
        for i in Account.objects.filter(company=user.company):
            Query = Lead.objects.filter(is_active=True, created_user=i, created_user__company=user.company, **d_f_kwargs)
            count = Query.count()
            summ = Query.aggregate(Sum('price'))['price__sum']
            t = {
                'id': i.id,
                'first_name': i.first_name,
                'last_name': i.last_name,
                'count': count,
                'summ': 0
            }
            if summ:
                t['summ'] = summ
            users_data.append(t)

        lead_filter_kw = {}
        lead_action_kw = {}
        if request.user.is_director:
            if user_pk == 0:
                lead_filter_kw['created_user__company'] = user.company
                lead_action_kw['changer__company'] = user.company
            else:
                lead_filter_kw['created_user_id'] = user_pk
                lead_action_kw['changer_id'] = user_pk
        else:
            lead_filter_kw['created_user'] = user
            lead_action_kw['changer'] = user
        Query = Lead.objects.filter(is_active=True, **lead_filter_kw, **d_f_kwargs)
        QAction = LeadAction.objects.filter(**lead_action_kw, **d_f_kwargs)
        TQ = Task.objects.filter(**lead_filter_kw, **d_f_kwargs)

        lead_query = Query.filter(status__lt=4).values('pole') \
            .annotate(count=Count(F('pole')), summa=Sum(F("price")))
        leadActionQuery = QAction.filter(newStatus=4).values('lead__pole', 'newStatus') \
            .annotate(count=Count(F('newStatus')), summa=Sum(F("lead__price")))

        leadPoles = LeadPoles.objects.filter(company=user.company)
        leadPoles_data = []
        for pole in leadPoles:
            dic = {
                "pole": pole.id,
                "count": 0,
                "summa": 0,
                "losed_count": 0,
                "losed_summa": 0,
            }
            for item in lead_query:
                if item['pole'] == pole.id:
                    dic["count"] = item['count']
                    dic["summa"] = item['summa']
            for item in leadActionQuery:
                if item['lead__pole'] == pole.id:
                    dic["losed_count"] = item['count']
                    dic["losed_summa"] = item['summa']

            leadPoles_data.append(dic)
        dt = {
            'losed': {
                'count': Query.filter(status=4).count(),
                'summa': Query.filter(status=4).aggregate(Sum('price'))['price__sum'],
            },
            'finished': {
                'count': Query.filter(status=5).count(),
                'summa': Query.filter(status=5).aggregate(Sum('finishedPrice'))['finishedPrice__sum'],
            },
            'task': {
                'register': TQ.filter(status=0).count(),
                'doing': TQ.filter(status=1).count(),
                'done': TQ.filter(status=2).count(),
                'deleted': TQ.filter(status=3).count(),
            },
            'lead_poles_data': leadPoles_data,
            'users': users_data
        }
        return JsonResponse(dt)
    except:
        return JsonResponse({"message": "error"})

@login_required
def main_is_influencer(request):
    try:
        # types = ((1, "Bugunlik"), (2, "Haftalik"), (3, "Oylik"), (4, "Sana range"))
        user_pk = int(request.GET.get('pk'))
        type = int(request.GET.get('type'))
        sana = datetime.today().date()
        if type == 1:
            sana1 = datetime(snaa.year, sana.month, sana.day)
            sana2 = datetime.fromordinal(sana.toordinal() + 1)
        elif type == 2:
            sana1 = datetime.fromordinal(sana.toordinal() - 6)
            sana2 = datetime.fromordinal(sana.toordinal() + 1)
        elif type == 3:
            sana1 = datetime.fromordinal(sana.toordinal() - 29)
            sana2 = datetime.fromordinal(sana.toordinal() + 1)
        elif type == 4:
            date1 = request.GET.get('sana1')
            date2 = request.GET.get('sana2')
            dt1 = date1.split('/')
            dt2 = date2.split('/')
            sana1 = datetime(int(dt1[2]), int(dt1[0]), int(dt1[1]))
            sana2 = datetime(int(dt2[2]), int(dt2[0]), int(dt2[1]))
        else:
            return Response({"message": "type error"})
        user = request.user
        d_f_kwargs = {
            "date__gte": sana1,
            "date__lt": sana2,
        }
        users_data = []
        for i in Account.objects.filter(company=user.company, is_influencer=True):
            Query = Lead.objects.filter(is_active=True, created_user=i, created_user__company=user.company, **d_f_kwargs)
            count = Query.count()
            summ = Query.aggregate(Sum('price'))['price__sum']
            t = {
                'id': i.id,
                'first_name': i.first_name,
                'last_name': i.last_name,
                'count': count,
                'summ': 0
            }
            if summ:
                t['summ'] = summ
            users_data.append(t)

        lead_filter_kw = {}
        lead_action_kw = {}
        if request.user.is_director:
            if user_pk == 0:
                lead_filter_kw['created_user__company'] = user.company
                lead_action_kw['changer__company'] = user.company
            else:
                lead_filter_kw['created_user_id'] = user_pk
                lead_action_kw['changer_id'] = user_pk
        else:
            lead_filter_kw['created_user'] = user
            lead_action_kw['changer'] = user
        Query = Lead.objects.filter(is_active=True, created_user__is_influencer=True, **lead_filter_kw, **d_f_kwargs)
        QAction = LeadAction.objects.filter(**lead_action_kw, **d_f_kwargs)
        TQ = Task.objects.filter(**lead_filter_kw, **d_f_kwargs)

        lead_query = Query.filter(status__lt=4).values('pole') \
            .annotate(count=Count(F('pole')), summa=Sum(F("price")))
        leadActionQuery = QAction.filter(newStatus=4).values('lead__pole', 'newStatus') \
            .annotate(count=Count(F('newStatus')), summa=Sum(F("lead__price")))

        leadPoles = LeadPoles.objects.filter(company=user.company)
        leadPoles_data = []
        for pole in leadPoles:
            dic = {
                "pole": pole.id,
                "count": 0,
                "summa": 0,
                "losed_count": 0,
                "losed_summa": 0,
            }
            for item in lead_query:
                if item['pole'] == pole.id:
                    dic["count"] = item['count']
                    dic["summa"] = item['summa']
            for item in leadActionQuery:
                if item['lead__pole'] == pole.id:
                    dic["losed_count"] = item['count']
                    dic["losed_summa"] = item['summa']

            leadPoles_data.append(dic)
        dt = {
            'losed': {
                'count': Query.filter(status=4).count(),
                'summa': Query.filter(status=4).aggregate(Sum('price'))['price__sum'],
            },
            'finished': {
                'count': Query.filter(status=5).count(),
                'summa': Query.filter(status=5).aggregate(Sum('finishedPrice'))['finishedPrice__sum'],
            },
            'task': {
                'register': TQ.filter(status=0).count(),
                'doing': TQ.filter(status=1).count(),
                'done': TQ.filter(status=2).count(),
                'deleted': TQ.filter(status=3).count(),
            },
            'lead_poles_data': leadPoles_data,
            'users': users_data
        }
        return JsonResponse(dt)
    except:
        return JsonResponse({"message": "error"})


def addtoken(request):
    t = request.POST['token']
    a = Account.objects.get(company=request.user.company, is_director=True)
    a.company.tg_token = t
    a.save()
    return redirect('setting')


def addsms(request):
    n = request.POST['nickname']
    c = request.POST['callback']
    email = request.POST['email']
    password = request.POST['password']
    company = Company.objects.get(id=request.user.company.id)

    company.sms_from = n
    company.sms_activated = False
    company.sms_callback_url = c
    company.sms_email = email
    company.sms_password = password
    response = requests.post('http://notify.eskiz.uz/api/auth/login', data={
        "email": email,
        "password": password,
    })
    if response.status_code == 200:
        company.sms_activated = True
        company.sms_token = response.json()['data']['token']
        response2 = requests.get('http://notify.eskiz.uz/api/auth/user', headers={
            "Authorization": f"Bearer {company.sms_token}",
        })
        if response2.status_code == 200:
            company.sms_balans = response2.json()['data']['balance']
    company.save()
    return redirect('setting')


def addsmsto(request):
    client_id = request.POST['client_id']
    secret = request.POST['secret']
    sender_id = request.POST['sender_id']
    company = Company.objects.get(id=request.user.company.id)

    company.smsto_client_id = client_id
    company.smsto_secret = secret
    company.smsto_sender_id = sender_id

    response = requests.post('https://auth.sms.to/oauth/token', data={
        "client_id": client_id,
        "secret": secret,
        "expires_in": company.smsto_expires_in,
    })
    company.smsto_activated = False
    if response.status_code == 200:
        company.smsto_token = response.json()['jwt']
    company.save()
    return redirect('setting')


def EditUser(request):
    r = request.POST
    id = r['id']
    ism = r['ism']
    fam = r['fam']
    phone = r['phone']
    birthday = r['date']
    tg_id = r['tg_id']
    a = Lead.objects.get(id=id)
    a.name = ism
    a.surname = fam
    a.phone = phone
    a.birthday = birthday
    a.tg_id = tg_id
    a.save()
    url = '/edit/?id=' + str(id)
    return redirect(url)


def GetRegion(request):
    id = request.GET.get('id')
    dist = District.objects.filter(region_id=id)
    dis = []
    for d in dist:
        t = {
            'id': d.id,
            'name': d.name
        }
        dis.append(t)

    data = {
        'district': dis
    }
    return JsonResponse(data)


def GetHodim(request):
    pk = request.GET.get('id')
    us = Account.objects.get(id=pk)
    dis = {
        'id': us.id,
        'fam': us.last_name,
        'ism': us.first_name
    }

    data = {
        'user': dis
    }
    return JsonResponse(data)


def EditHodim(request):
    r = request.POST
    id = r['id']
    fam = r['fam']
    ism = r['ism']
    username = r['username']
    password = r['password']
    status = r['status']
    us = Account.objects.get(id=id)
    try:
        Account.objects.get(username=username)
        messages.error(request, 'Loginni o`zgartiring')
        return redirect('setting')
    except:
        us.username = username
    if status == 'is_director':
        us.is_director = True
    elif status == 'is_influencer':
        us.is_influencer = True
        
    us.first_name = ism
    us.last_name = fam
    us.password = make_password(password)
    us.save()
    messages.success(request, 'Hodim taxrirlandi')
    return redirect('setting')


def edit_userleadpoles(request):
    if request.method == "POST":
        user_id = request.POST.get("id")
        user = Account.objects.get(id=user_id)

        # lead_ids ni POST dan ajratib olish
        lead_ids = [
            int(key.split("_")[1])
            for key in request.POST.keys()
            if key.startswith("lead_")
        ]
        leads = LeadPoles.objects.filter(id__in=lead_ids)

        # faqat leadpoles yangilanadi
        user.leadpoles.set(leads)
        user.save()

        messages.success(request, "Hodimning ruhsatlari yangilandi")
        return redirect("setting")




import redis

# r = redis.StrictRedis(host='localhost', port=6379, db=0)
# print(r.ping())


# for i in Calendar.objects.all()[:1]:
#     text = "Eslatma \n"
#     text += f"\nMijoz: {i.user.name}"
#     text += f"\nYaratti: {i.created_user.first_name}"
#     text += f"\nEslatma: {i.event}"

#     print(text)


from django.shortcuts import render, redirect, get_object_or_404

# def add_complaint(request):
#     if request.method == 'POST':
#         lead_id = request.POST.get('lead_id')
#         complaint_type = request.POST.get('type')
#         text = request.POST.get('text')
#         date = request.POST.get('date')
        
#         lead = get_object_or_404(Lead, id=lead_id)
#         Complaint.objects.create(
#             lead=lead,
#             type=complaint_type,
#             text=text,
#             date=date,
#             status='pending'
#         )
#         messages.success(request, ('Complaint/objection added successfully'))
#         return redirect(request.META.get('HTTP_REFERER', '/'))
    
#     return redirect('/')

# def edit_complaint(request, complaint_id):
#     complaint = get_object_or_404(Complaint, id=complaint_id)
    
#     if request.method == 'POST':
#         complaint.type = request.POST.get('type', complaint.type)
#         complaint.text = request.POST.get('text', complaint.text)
#         complaint.date = request.POST.get('date', complaint.date)
#         complaint.status = request.POST.get('status', complaint.status)
#         complaint.save()
        
#         messages.success(request, ('Complaint updated successfully'))
#         return redirect(request.META.get('HTTP_REFERER', '/'))
    
#     return redirect('/')

# def delete_complaint(request, complaint_id):
#     if request.method == 'POST':
#         complaint = get_object_or_404(Complaint, id=complaint_id)
#         complaint.delete()
#         messages.success(request, ('Complaint deleted successfully'))
#         return JsonResponse({'success': True})
    
#     return JsonResponse({'success': False}, status=400)


def complaints_list(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    complaints = lead.complaints.all().order_by('-date')
    
    context = {
        'lead': lead,
        'complaints': complaints,
        'LANGUAGE_CODE': request.LANGUAGE_CODE
    }
    return render(request, 'complaints/complaints_list.html', context)

def add_complaint(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        complaint_type = request.POST.get('type')
        text = request.POST.get('text')
        date = request.POST.get('date')
        
        lead = get_object_or_404(Lead, id=lead_id)
        Complaint.objects.create(
            lead=lead,
            type=complaint_type,
            text=text,
            date=date,
            status='pending'
        )
        
        # Messages in all three languages
        if request.LANGUAGE_CODE == 'en':
            messages.success(request, 'Complaint/objection added successfully')
        elif request.LANGUAGE_CODE == 'ru':
            messages.success(request, 'Жалоба/возражение успешно добавлена')
        else:
            messages.success(request, 'Shikoyat/etiroz muvaffaqiyatli qo\'shildi')
            
    
    return redirect(request.META['HTTP_REFERER'])

def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        complaint.type = request.POST.get('type', complaint.type)
        complaint.text = request.POST.get('text', complaint.text)
        complaint.date = request.POST.get('date', complaint.date)
        complaint.status = request.POST.get('status', complaint.status)
        complaint.save()
        
        if request.LANGUAGE_CODE == 'en':
            messages.success(request, 'Complaint updated successfully')
        elif request.LANGUAGE_CODE == 'ru':
            messages.success(request, 'Жалоба успешно обновлена')
        else:
            messages.success(request, 'Shikoyat muvaffaqiyatli yangilandi')
            
    
    return redirect(request.META['HTTP_REFERER'])

# def delete_complaint(request, complaint_id):
#     if request.method == 'POST':
#         complaint = get_object_or_404(Complaint, id=complaint_id)
#         lead_id = complaint.lead.id
#         complaint.delete()
        
#         # Messages in all three languages
#         if request.LANGUAGE_CODE == 'en':
#             messages.success(request, 'Complaint deleted successfully')
#         elif request.LANGUAGE_CODE == 'ru':
#             messages.success(request, 'Жалоба успешно удалена')
#         else:
#             messages.success(request, 'Shikoyat muvaffaqiyatli o\'chirildi')
            
    
#     return redirect(request.META['HTTP_REFERER'])

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt 
def delete_complaint(request, pk):
    try:
        complaint = Complaint.objects.get(pk=pk)
        complaint.delete()
        return JsonResponse({'status': 'success'})
    except Complaint.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Shikoyat topilmadi'}, status=404)



def call_logs(request):
    context = {
        'company': request.user.company
    }
    return render(request, 'call_logs.html', context)


def search_phone_number_lead(request):
    phone = request.GET.get('phone')[-9:]
    lead = Lead.objects.filter(Q(phone__endswith=phone) | Q(phone2__endswith=phone)| Q(telegram_phone_number__endswith=phone)).last()
    return JsonResponse({'id':lead.id})


@login_required
def add_moizvonki(request):
    if request.method == 'POST':
        user_name = request.POST.get('zvonki_user_name')
        api_key = request.POST.get('zvonki_api_key')
        name = request.POST.get('zvonki_name')
        
        company = get_object_or_404(Company, id=request.user.company.id)
        
        company.zvonki_user_name = user_name
        company.zvonki_api_key = api_key
        company.zvonki_name = name
        company.save()
        
        messages.success(request, "Moizvonki ma'lumotlari muvaffaqiyatli saqlandi.")
        return redirect(request.META.get('HTTP_REFERER'))




def add_new_complaint(request):
    complaint = request.POST.get('complaint')
    lead_id = request.POST.get('lead_id')
    NewComplaints.objects.create(complaint=complaint, lead_id=lead_id, who_accepted=request.user)
    return redirect(request.META.get('HTTP_REFERER'))


def edit_new_complaint(request, id):
    complaint = request.POST.get('complaint')
    NewComplaints.objects.filter(id=id).update(complaint=complaint)
    return redirect(request.META.get('HTTP_REFERER'))

def del_new_complaint(request, id):
    NewComplaints.objects.get(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def change_status_new_complaint(request, id):
    status = request.POST.get('status')
    new =  NewComplaints.objects.get(id=id)
    new.status = status
    new.close_time = datetime.now()
    new.save()
    return JsonResponse({'ok':'ok'})



def add_new_objections(request):
    objection = request.POST.get('objection')
    answer = request.POST.get('answer')
    lead_id = request.POST.get('lead_id')
    NewObjections.objects.create(
        objection=objection,
        answer=answer,
        who_accepted=request.user,
        lead_id=lead_id,
    )
    return redirect(request.META.get('HTTP_REFERER'))

def edit_new_objections(request, id):
    objection = request.POST.get('objection')
    answer = request.POST.get('answer')
    NewObjections.objects.filter(id=id).update(
        objection = objection,
        answer = answer,
    )
    return redirect(request.META.get('HTTP_REFERER'))

def del_new_objections(request, id):
    NewObjections.objects.get(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER'))


def add_client_benefits(request):
    benefit = request.POST.get('benefit')
    lead_id = request.POST.get('lead_id')
    ClientBenefits.objects.create(benefit=benefit, lead_id=lead_id, who_accepted=request.user,)
    return redirect(request.META.get('HTTP_REFERER'))


def edit_client_benefits(request, id):
    benefit = request.POST.get('benefit')
    ClientBenefits.objects.filter(id=id).update(benefit=benefit)
    return redirect(request.META.get('HTTP_REFERER'))

def del_client_benefits(request, id):
    ClientBenefits.objects.get(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER'))


def add_why_buy(request):
    reason = request.POST.get('reason')
    lead_id = request.POST.get('lead_id')
    WhyBuy.objects.create(reason=reason, lead_id=lead_id, who_accepted=request.user,)
    return redirect(request.META.get('HTTP_REFERER'))


def edit_why_buy(request, id):
    reason = request.POST.get('reason')
    WhyBuy.objects.filter(id=id).update(reason=reason)
    return redirect(request.META.get('HTTP_REFERER'))

def del_why_buy(request, id):
    WhyBuy.objects.get(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER'))

from django.db.models import ExpressionWrapper, DurationField, Avg

import time

def customer_analysis(request):
    complaints = NewComplaints.objects.filter(who_accepted__company_id=request.user.company.id)
    objections = NewObjections.objects.filter(who_accepted__company_id=request.user.company.id)
    benefits = ClientBenefits.objects.filter(who_accepted__company_id=request.user.company.id)
    why_buy = WhyBuy.objects.filter(who_accepted__company_id=request.user.company.id)

    total_time_avg = complaints.filter(close_time__isnull=False).annotate(
        time_diff = ExpressionWrapper(F('close_time')-F('created_add'), output_field=DurationField())
    ).aggregate(avg=Avg('time_diff'))['avg']

    total_time_com = complaints.filter(close_time__isnull=False).annotate(
        time_diff=ExpressionWrapper(F('close_time') - F('created_add'), output_field=DurationField())
    ).aggregate(total=Sum('time_diff'))['total']

    formatted_avg = "00:00:00"
    if total_time_avg:
        total_secund_avg = int(total_time_avg.total_seconds())
        avg_hour, ramend = divmod(total_secund_avg, 3600)
        avg_minut, seconds = divmod(total_secund_avg, 60)
        formatted_avg = f"{avg_hour:02}:{avg_minut:02}:{seconds:02}"
        

    format_total = "00:00:00"
    if total_time_com:
        total_second = int(total_time_com.total_seconds())
        total_hour_comp, remand = divmod(total_second, 3600)
        total_minut_comp, total_second_comp = divmod(total_second, 60)
        format_total = f"{total_hour_comp:02}:{total_minut_comp:02}:{total_second_comp:02}"


    if benefits.count() >= 2:
        one_first = benefits[0].created_add
        two_first = benefits[1].created_add
        delta = one_first - two_first
        total_minutes = int(delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        time_diff = f"{hours} soat {minutes} daqiqa"
    else:
        time_diff = ""

    data = [
        {
            'category':1,
            'count':complaints.count(),
            'lead_count':complaints.values('lead').count(),
            'total_time_avg':formatted_avg,
            'format_total':format_total,
        },
        {
            'category':2,
            'count':objections.count(),
            'lead_count':objections.values('lead').count(),
        },
        {
            'category':3,
            'count':benefits.count(),
            'lead_count':benefits.values('lead').count(),
            'first':benefits.first(),
            'tow':time_diff,
        },
        {
            'category':4,
            'count':why_buy.count(),
            'lead_count':why_buy.values('lead').count(),
        },
    ]
    context = {
        'complaints': complaints,
        'new_objections':objections,
        'client_benefits':benefits,
        'why_buy':why_buy,
        'data':data,
    }
               
    return render(request, 'customer_analysis.html', context)