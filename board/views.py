import json
from datetime import datetime, timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin
from django.db.models import Count, Q, F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Account, Company
from account.functions import sms_text_replace, checkPhone, sendSmsOneContact
from board.models import Lead, LeadAction, Task, Telegram_user, LeadPoles, SMSTemplate, SMS_template_choise, \
    UrlRedirect, NoteForm, FormQuestion, FormAnswer, AnswerQuestion, Product, Payment_type, Shopping, Region, District, Instruktsya, Referral
from board.serializers import LeadSerializer, TaskSerializer, CompanySerializer, Telegram_userSerializer
import xlwt


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    wb = xlwt.Workbook(encoding='utf-8')

    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font

    lead_poles = LeadPoles.objects.filter(company=request.user.company)
    for pole in lead_poles:
        row_num = 1
        ws = wb.add_sheet(pole.name)
        columns = ["Ro'yxatga olingan sana", "Nomi", "Telefon", "Qo'shimcha telefon", "Ro'yxatga olgan user"]
        columnsNested = ["", "Sana", "Mahsulot", "Soni", "Narxi", "Summa", "To'lov turi", "Izoh"]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style=style)
        leads = Lead.objects.filter(is_active=True, status=0, pole=pole, created_user__company=request.user.company)
        shoppings = Shopping.objects.filter(lead__created_user__company=request.user.company)
        for lead in leads:
            row_num += 1
            ws.write(row_num, 0, str(lead.date.strftime("%Y-%m-%d %H:%M:%S")))
            ws.write(row_num, 1, lead.name)
            ws.write(row_num, 2, lead.phone)
            ws.write(row_num, 3, lead.phone2)
            ws.write(row_num, 4, lead.created_user.first_name)
            nestedBor = False
            for shop in shoppings:
                if shop.lead == lead:
                    if not nestedBor:
                        row_num += 1
                        ws.write(row_num, 3, "Sotilgan mahsulotlar", style=style)
                        row_num += 1
                        for col_num in range(len(columnsNested)):
                            ws.write(row_num, col_num, columnsNested[col_num], style=style)
                        nestedBor = True
                    row_num += 1
                    ws.write(row_num, 1, shop.date.strftime("%Y-%m-%d %H:%M"))
                    ws.write(row_num, 2, shop.product.name)
                    ws.write(row_num, 3, shop.count)
                    ws.write(row_num, 4, shop.price)
                    ws.write(row_num, 5, shop.amount)
                    ws.write(row_num, 6, shop.payment_type.name)
                    ws.write(row_num, 7, shop.comment)
    response['Content-Disposition'] = f'attachment; filename="Leads ' \
                                      f'{datetime.today().strftime("%Y-%m-%d %H-%M-%S")}.xls"'
    wb.save(response)

    return response


def register_lead_send_sms(lead: Lead):
    template = SMSTemplate.objects.filter(
        active=True, company__active=True, type=SMS_template_choise[0][0],
        company=lead.created_user.company
    ).first()
    if template:
        text = sms_text_replace(template.text, lead)
        can, phone = checkPhone(lead.phone)
        if can:
            sendSmsOneContact(template.company, lead.phone, text)


# Telegram bot uchun boshlanishi <<<<<<<<<


@api_view(['GET'])
def telegram_bot_get_company(request):
    try:
        token = request.GET.get('token')
        chat_id = int(request.GET.get('chat_id'))
        company = Company.objects.filter(tg_token=token).first()
        if Telegram_user.objects.filter(chat_id=chat_id, token=token).count() == 0:
            userr = Telegram_user.objects.create(
                chat_id=chat_id,
                token=token
            )
            return Response({
                "company": CompanySerializer(company).data,
                "user": Telegram_userSerializer(userr).data
            })
        else:
            return Response({
                "company": CompanySerializer(company).data,
                "user": Telegram_userSerializer(Telegram_user.objects.filter(chat_id=chat_id).first()).data
            })
    except:
        return Response({"message": "Error"}, 404)


@api_view(['GET'])
def telegram_bot_add_phone(request):
    try:
        phone = request.GET.get('phone')
        token = request.GET.get('token')
        chat_id = int(request.GET.get('chat_id'))
        user = Telegram_user.objects.filter(chat_id=chat_id, token=token).first()
        user.step = 2
        user.phone = phone
        user.save()
        return Response({
            "user": Telegram_userSerializer(user).data
        })
    except:
        return Response({"message": "Error"}, 404)


@api_view(['GET'])
def telegram_bot_add_name(request):
    try:
        name = request.GET.get('name')
        token = request.GET.get('token')
        chat_id = int(request.GET.get('chat_id'))
        user = Telegram_user.objects.filter(chat_id=chat_id, token=token).first()
        user.step = 3
        user.name = name
        user.save()
        return Response({
            "user": Telegram_userSerializer(user).data
        })
    except:
        return Response({"message": "Error"}, 404)


@api_view(['GET'])
def telegram_bot_add_company(request):
    try:
        company = request.GET.get('company')
        token = request.GET.get('token')
        chat_id = int(request.GET.get('chat_id'))
        user = Telegram_user.objects.filter(chat_id=chat_id, token=token).first()
        user.step = 4
        user.company = company
        user.save()
        return Response({
            "user": Telegram_userSerializer(user).data
        })
    except:
        return Response({"message": "Error"}, 404)


@api_view(['GET'])
def telegram_bot_add_company_address(request):
    try:
        companyadd = request.GET.get('companyaddress')
        token = request.GET.get('token')
        chat_id = int(request.GET.get('chat_id'))
        user = Telegram_user.objects.filter(chat_id=chat_id, token=token).first()
        user.step = 5
        user.companyAddress = companyadd
        user.save()
        return Response({
            "user": Telegram_userSerializer(user).data
        })
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
def create_lead_by_tg(request):
    try:
        data = request.data
        name = data['name']
        company = data['company']
        address = data['address']
        phone = data['phone']
        tg_token = data['token']
        phone = str(phone).replace('+', '')
        tg_chatid = int(data['tg_chatid'])
        if Lead.objects.filter(is_active=True, tg_chatid=tg_chatid, created_user__company__tg_token=tg_token).count() == 0:
            companyCOm = Company.objects.filter(tg_token=tg_token).first()
            created_user = Account.objects.filter(company=companyCOm, is_director=True).first()
            lead = Lead.objects.create(
                name=name,
                company=company,
                phone=phone,
                companyAddress=address,
                created_user=created_user,
                joinBy=1,
                tg_chatid=tg_chatid
            )
            LeadAction.objects.create(lead=lead, changer=created_user)
            register_lead_send_sms(lead)
            return Response({
                "user": LeadSerializer(lead).data
            })
        else:
            return Response({"message": "Error"}, 501)

    except:
        return Response({"message": "Error"}, 404)


# Telegram bot uchun tugashi >>>>>>>>
def is_B2B(request):
    return request.user.company.type == "B2B"


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_lead(request):
    try:
        print(1111)
        data = request.data
        pole = LeadPoles.objects.filter(company=request.user.company).first()
        name = data['name']
        validity_period = data.get('validity_period')
        price = int(data['price'])
        user = int(data['user'])
        phone = data.get('phone')
        referral = data.get('referral')
        print(phone)
        print(validity_period)
        if is_B2B(request):
            company = data['company']
            address = data.get('address')

            lead = Lead.objects.create(name=name,
                                       price=price,
                                       company=company,
                                       district_id=address,
                                       pole=pole,
                                       phone=phone,
                                       created_user_id=user,
                                       referral_id=referral,
                                       validity_period=validity_period if validity_period else None)
        else:
            
            lead = Lead.objects.create(name=name,
                                       price=price,
                                       phone=phone,
                                       pole=pole,
                                       district_id=address,
                                       created_user_id=user,
                                       referral_id=referral,
                                        validity_period=validity_period if validity_period else None)
        LeadAction.objects.create(lead=lead, changer_id=user)
        register_lead_send_sms(lead)

        return Response(LeadSerializer(lead).data)
    except Exception as ex:
        print("Xatolik:", ex)
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def edit_lead(request):
    try:
        data = request.data
        leadId = int(data['lead'])
        name = data['name']
        price = int(data['price'])
        user = int(data['user'])
        phone = data.get('phone')
        lead = Lead.objects.get(id=leadId)
        lead.name = name
        lead.price = price
        company = data['company']
        address = data['address']
        lead.company = company
        lead.companyAddress = address
        print(phone)
        lead.phone = phone
        LeadAction.objects.create(lead=lead, changer_id=user, status=1)
        lead.save()

        return Response(LeadSerializer(lead).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_lead_status(request):
    try:
        data = request.data
        izoh = data['izoh']
        leadID = int(data['lead'])
        user = int(data['user'])
        new_pole = int(data['status'])
        lead = Lead.objects.get(id=leadID)
        LeadAction.objects.create(lead=lead, changer_id=user, note=izoh,
                                  oldpole_id=lead.pole_id,
                                  newpole_id=new_pole, status=4)
        lead.pole_id = new_pole
        lead.save()
        return Response(LeadSerializer(lead).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lead_finished(request):
    try:
        data = request.data
        price = int(data['price'])
        leadID = int(data['lead'])
        user = int(data['user'])
        lead = Lead.objects.get(id=leadID)
        LeadAction.objects.create(lead=lead, changer_id=user, oldStatus=lead.status, newStatus=5, status=2)
        lead.status = 5
        lead.finishedPrice = price
        lead.finishedDate = datetime.now(timezone.utc)
        lead.save()
        return Response(LeadSerializer(lead).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lead_losed(request):
    try:
        data = request.data
        izoh = data['izoh']
        leadID = int(data['lead'])
        user = int(data['user'])
        lead = Lead.objects.get(id=leadID)
        LeadAction.objects.create(lead=lead, changer_id=user, note=izoh, oldStatus=lead.status, newStatus=4, status=2)
        lead.status = 4
        lead.save()
        return Response(LeadSerializer(lead).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        data = request.data
        name = data['name']
        user = int(data['user'])
        task = Task.objects.create(name=name, created_user_id=user)
        return Response(TaskSerializer(task).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_task_status(request):
    try:
        data = request.data
        taskId = int(data['task'])
        status = int(data['status'])
        task = Task.objects.get(id=taskId)
        task.status = status
        if status == 2:
            task.finishedDate = datetime.now(timezone.utc)
        task.save()
        return Response(TaskSerializer(task).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def note_task(request):
    try:
        data = request.data
        taskId = int(data['task'])
        note = data['note']
        task = Task.objects.get(id=taskId)
        task.note = note
        task.save()
        return Response(TaskSerializer(task).data)
    except:
        return Response({"message": "Error"}, 404)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_lead_count(request):
    try:
        data = request.data
        status = list(json.loads(data['status']))
        pole_list = list(json.loads(data['pole_list']))
        LeadsCount = Lead.objects \
            .filter(created_user__company=request.user.company) \
            .filter(Q(status__in=status) | (Q(status=0) & Q(
            pole_id__in=pole_list))).count()
        # status=0 bolishi kerak lead bordda bo'lishi uchun
        return Response({"count": LeadsCount})
    except:
        return Response({"message": "Error"}, 404)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def check_pole_can_delete(request):
    try:
        pole_id = int(request.GET['pole_id'])
        leads = list(Lead.objects.filter(is_active=True, pole_id=pole_id).values(
            'created_user__username'
        ).annotate(
            count=Count('pole_id')
        ))
        if len(leads) > 0:
            return Response({"data": leads, "status": 500})
        else:
            return Response({"data": [], "status": 200})

    except:
        return Response({"data": [], "status": 505})


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_pole(request):
    try:
        pole_id = int(request.POST['pole_id'])
        count = Lead.objects.filter(is_active=True, pole_id=pole_id).count()
        if count == 0:
            LeadPoles.objects.get(id=pole_id).delete()

        return Response({"status": 200})
    except:
        return Response({"status": 505})


@login_required
def add_pole(request):
    try:
        if request.user.is_director:
            if request.POST['name'] != "":
                LeadPoles.objects.create(company=request.user.company, name=request.POST['name'])
    except:
        pass
    return redirect('board')


@login_required
def edit_pole(request):
    try:
        if request.user.is_director:
            pole = LeadPoles.objects.get(id=int(request.POST['id']))
            pole.name = request.POST['name']
            pole.number = request.POST['number']
            pole.save()
    except:
        pass
    return redirect('board')


class Board(TemplateView, AccessMixin):
    template_name = 'Board.html'

    def get_context_data(self, *args, **kwargs):
        super(Board, self).get_context_data(**kwargs)

        region = self.request.GET.get('region')
        district = self.request.GET.get('district')
        users = self.request.GET.get('users')
        date_range = self.request.GET.get('date')
        print(date_range)
        if self.request.user.is_director:
            leads = Lead.objects.filter(is_active=True, status__lt=4, created_user__company=self.request.user.company)
        else:
            leads = Lead.objects.filter(is_active=True, status__lt=4, created_user__company=self.request.user.company, created_user=self.request.user)

        lead_poles = LeadPoles.objects.filter(company=self.request.user.company)

        
        if district:
            print(22)
            leads = leads.filter(district__id=district)

        if users:
            print(11)
            leads = leads.filter(created_user__id=users)

        if date_range:
            start_str, end_str = date_range.split(' - ')
            start_date = datetime.strptime(start_str, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_str, '%m/%d/%Y').date()
            
            leads = leads.filter(date__date__range=(start_date, end_date))

        all_lead = []
        if self.request.user.company.type == "B2B":
            for i in leads:
                all_lead.append(
                    {"id": i.id,
                     "name": i.name,
                     "date": i.date.strftime("%Y-%m-%d, %H:%M"),
                     "price": i.price,
                     "company": i.company,
                     "address": i.companyAddress
                     }
                )
        else:
            for i in leads:
                all_lead.append(
                    {"id": i.id,
                     "name": i.name,
                     "date": i.date.strftime("%Y-%m-%d, %H:%M"),
                     "price": i.price,
                     "phone": i.phone,
                     }
                )

        context = {
            "Board": "active",
            "leads": leads,
            "all_leads": json.dumps(all_lead),
            "lead_poles": lead_poles,

            'region': Region.objects.all(),
            'district': District.objects.all(),
            'users' : Account.objects.filter(company=self.request.user.company),
            'referral' : Referral.objects.filter(company=self.request.user.company)
        }
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class TaskClass(TemplateView, AccessMixin):
    template_name = 'task.html'

    def get_context_data(self, *args, **kwargs):
        super(TaskClass, self).get_context_data(**kwargs)
        tasks = Task.objects.filter(status__lt=2, created_user=self.request.user)
        group1 = tasks.filter(status=0)
        group2 = tasks.filter(status=1)
        all_tasks = []
        for i in tasks:
            all_tasks.append({
                "id": i.id,
                "name": i.name,
                "date": i.date.strftime("%Y-%m-%d, %H:%M"),
                "note": i.note
            })

        context = {
            "Task": "active",
            "group1": group1,
            "group2": group2,
            "all_tasks": json.dumps(all_tasks)
        }
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class Redirect_class(TemplateView, AccessMixin):
    template_name = 'redirect/list.html'

    def get_context_data(self, *args, **kwargs):
        super(Redirect_class, self).get_context_data(**kwargs)
        urlRedirects = UrlRedirect.objects.filter(company=self.request.user.company)
        formRedirects = NoteForm.objects.filter(company=self.request.user.company)
        context = {
            "redirect": "active",
            "urlRedirects": urlRedirects,
            "formRedirects": formRedirects,
        }
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class NewUrlRedirect_class(TemplateView, AccessMixin):
    template_name = 'redirect/add.html'

    def post(self, *args, **kwargs):
        try:
            name = self.request.POST['name']
            next_url = self.request.POST['next_url']
            url = UrlRedirect()
            url.company = self.request.user.company
            url.name = name
            url.next_url = next_url
            url.save()
        except:
            pass
        return redirect('redirect_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class EditUrlRedirect_class(TemplateView, AccessMixin):
    template_name = 'redirect/edit.html'
    url_redirect = None

    def post(self, *args, **kwargs):
        try:
            name = self.request.POST['name']
            next_url = self.request.POST['next_url']
            self.url_redirect.name = name
            self.url_redirect.next_url = next_url
            self.url_redirect.save()
        except:
            pass
        return redirect('redirect_list')

    def get_context_data(self, *args, **kwargs):
        context = super(EditUrlRedirect_class, self).get_context_data(**kwargs)
        context['url_redirect'] = self.url_redirect
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        pk = kwargs['pk']
        try:
            self.url_redirect = UrlRedirect.objects.get(company=self.request.user.company, id=pk)
        except UrlRedirect.DoesNotExist:
            return redirect("redirect_list")
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


def redirect_view(request):
    try:
        pk = int(request.GET['pk'])
        next_url = request.GET['next_url']
        social = request.GET['social']
        if social == "telegram":
            UrlRedirect.objects.filter(id=pk) \
                .update(total_count=F('total_count') + 1,
                        telegram_count=F('telegram_count') + 1)
        if social == "instagram":
            UrlRedirect.objects.filter(id=pk) \
                .update(total_count=F('total_count') + 1,
                        instagram_count=F('instagram_count') + 1)
        if social == "facebook":
            UrlRedirect.objects.filter(id=pk) \
                .update(total_count=F('total_count') + 1,
                        facebook_count=F('facebook_count') + 1)
        if social == "youtube":
            UrlRedirect.objects.filter(id=pk) \
                .update(total_count=F('total_count') + 1,
                        youtube_count=F('youtube_count') + 1)
        if social == "tiktok":
            UrlRedirect.objects.filter(id=pk) \
                .update(total_count=F('total_count') + 1,
                        tiktok_count=F('tiktok_count') + 1)

        return HttpResponseRedirect(next_url)
    except:
        return redirect('home')


def social_correct(text):
    for item in FormAnswer.social_choise:
        if item[0] == text:
            return True
    return False


class PublicNoteForm_class(TemplateView, AccessMixin):
    template_name = 'NoteForm/PublicNoteForm.html'

    def post(self, *args, **kwargs):
        try:
            pk = int(self.request.POST['noteForm'])
            noteForm = NoteForm.objects.get(pk=pk)
            social = self.request.POST['social']
            if social_correct(social):
                questions = FormQuestion.objects.filter(form=noteForm)
                success = True
                for question in questions:
                    if self.request.POST.get(f'name_{question.id}', None) is None:
                        success = False
                if success:
                    formAnswer = FormAnswer.objects.create(
                        form=noteForm,
                        join_by=social
                    )
                    for question in questions:
                        AnswerQuestion.objects.create(
                            question=question,
                            answer=formAnswer,
                            text=self.request.POST[f'name_{question.id}']
                        )
                    if social == "telegram":
                        noteForm.telegram_count += 1
                    if social == "instagram":
                        noteForm.instagram_count += 1
                    if social == "facebook":
                        noteForm.facebook_count += 1
                    if social == "youtube":
                        noteForm.youtube_count += 1
                    if social == "tiktok":
                        noteForm.tiktok_count += 1
                    noteForm.total_count += 1
                    noteForm.save()
                    messages.success(self.request, "Ma'lumotlaringiz yuborildi!")
        except:
            messages.error(self.request, "Xatolik")

        return redirect('PublicNoteForm_class')

    def get_context_data(self, *args, **kwargs):
        context = super(PublicNoteForm_class, self).get_context_data(**kwargs)
        try:
            pk = int(self.request.GET['pk'])
            social = self.request.GET['social']
            noteForm = NoteForm.objects.get(id=pk)
            questions = FormQuestion.objects.filter(form=noteForm)
            context['social'] = social
            context['noteForm'] = noteForm
            context['questions'] = questions
            context['success'] = True
            context['company'] = Company.objects.get(id=self.request.user.company.id)
        except:
            context['success'] = False
        return context


class NewFormRedirect_class(TemplateView, AccessMixin):
    template_name = 'NoteForm/add.html'

    def post(self, *args, **kwargs):
        try:
            name = self.request.POST['name']
            questions = self.request.POST.getlist('field')
            image = self.request.FILES['image']
            noteForm = NoteForm()
            noteForm.name = name
            noteForm.image = image
            noteForm.company = self.request.user.company
            noteForm.save()
            for question in questions:
                FormQuestion.objects.create(
                    form=noteForm,
                    name=question
                )
        except:
            pass
        return redirect('redirect_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class ShowFormResults_class(TemplateView, AccessMixin):
    template_name = 'NoteForm/showResults.html'
    noteForm = None

    def get_context_data(self, *args, **kwargs):
        context = super(ShowFormResults_class, self).get_context_data(**kwargs)
        questions = FormQuestion.objects.filter(form=self.noteForm)
        answers = FormAnswer.objects.filter(form=self.noteForm)
        answerQuestions = list(AnswerQuestion.objects.filter(answer__form=self.noteForm).values(
            'id', 'question', 'answer', 'text'
        ))
        formAnswers = []
        for answer in answers:
            answersQs = []
            for item in answerQuestions:
                if item['answer'] == answer.id:
                    answersQs.append(item)
            answerDic = {
                "id": answer.id,
                "date": answer.date.strftime("%Y-%m-%d %H:%M"),
                "join_by": answer.join_by,
                "answers": []
            }
            for question in questions:
                answerQ = None
                for item in answersQs:
                    if item['question'] == question.id:
                        answerQ = item
                if answerQ is not None:
                    answerDic['answers'].append(answerQ['text'])
                else:
                    answerDic['answers'].append("")
            formAnswers.append(answerDic)

        context['formAnswers'] = formAnswers
        context['questions'] = questions
        context['company'] = Company.objects.get(id=self.request.user.company.id)

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            pk = kwargs['pk']
            self.noteForm = NoteForm.objects.get(id=pk)
        except:
            return redirect('redirect_list')
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class AddShopping_class(TemplateView, AccessMixin):
    template_name = 'shopping/add.html'
    lead = None

    def post(self, *args, **kwargs):
        try:
            data = self.request.POST
            Shopping.objects.create(
                company=self.request.user.company,
                lead=self.lead,
                product_id=int(data['product']),
                count=int(data['count']),
                price=int(data['price']),
                payment_type_id=int(data['payment_type']),
                comment=data['comment'],
                amount=int(data['count']) * int(data['price']),
                account=self.request.user,
            )
        except:
            pass
        response = redirect('edit')
        response['Location'] += f'?id={self.lead.id}'
        return response

    def get_context_data(self, *args, **kwargs):
        context = super(AddShopping_class, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(company=self.request.user.company)
        context['payment_types'] = Payment_type.objects.filter(company=self.request.user.company)
        context['lead'] = self.lead
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            pk = kwargs['pk']
            self.lead = Lead.objects.get(id=pk)
        except:
            return redirect('board')
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


class EditShopping_class(TemplateView, AccessMixin):
    template_name = 'shopping/edit.html'
    lead = None
    shopping = None

    def post(self, *args, **kwargs):
        try:
            data = self.request.POST
            self.shopping.product_id = int(data['product'])
            self.shopping.count = int(data['count'])
            self.shopping.price = int(data['price'])
            self.shopping.payment_type_id = int(data['payment_type'])
            self.shopping.comment = data['comment']
            self.shopping.amount = int(data['count']) * int(data['price'])
            self.shopping.account = self.request.user
            self.shopping.save()
        except:
            pass
        response = redirect('edit')
        response['Location'] += f'?id={self.lead.id}'
        return response

    def get_context_data(self, *args, **kwargs):
        context = super(EditShopping_class, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(company=self.request.user.company)
        context['payment_types'] = Payment_type.objects.filter(company=self.request.user.company)
        context['lead'] = self.lead
        context['shopping'] = self.shopping
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            lead_pk = kwargs['pk']
            shop_pk = kwargs['shop_pk']
            self.lead = Lead.objects.get(id=lead_pk)
            self.shopping = Shopping.objects.get(id=shop_pk, company=self.request.user.company)
        except:
            return redirect('board')
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)


@login_required
def delete_simple_redirect(request, pk):
    try:
        urlRedirect = UrlRedirect.objects.get(id=pk)
        if urlRedirect.company == request.user.company:
            urlRedirect.delete()
    except:
        pass
    return redirect('redirect_list')


@login_required
def delete_form_redirect(request, pk):
    try:
        noteForm = NoteForm.objects.get(id=pk)
        if noteForm.company == request.user.company:
            AnswerQuestion.objects.filter(answer__form=noteForm).delete()
            noteForm.delete()

    except:
        pass
    return redirect('redirect_list')

class InstruktsyaList(TemplateView, AccessMixin):
    template_name = 'instruktsya_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(InstruktsyaList, self).get_context_data(**kwargs)
        instruktsya = Instruktsya.objects.filter(company=self.request.user.company)
        context['instruktsya'] = instruktsya
        return context



def instruktsya_add(request):
    title = request.POST.get('title')
    video_file = request.FILES.get('video_file')
    photo = request.FILES.get('photo')
    video_link = request.POST.get('video_link')
    text = request.POST.get('text')
    Instruktsya.objects.create(
        title=title,
        video_file=video_file,
        video_link=video_link,
        photo=photo,
        text=text,
        company=request.user.company
    )
    return redirect(request.META["HTTP_REFERER"])
    

def instruktsya_list_detail(request,id):
    context = {
        'item':Instruktsya.objects.get(id=id)
    }
    return render(request, 'instruktsya_list_detail.html', context)



import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def import_leads_from_excel(request):
    print(1111)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        print(222)
        excel_file = request.FILES['excel_file']
        print(3333)
        df = pd.read_excel(excel_file)

        column_mapping = {
            'Nomi': 'name',
            'Telefon Raqam': 'phone',
            'Summa': 'price',
            'Viloyat': 'region',
            'Hudud': 'district'
        }

        df = df.rename(columns=column_mapping)

        required_columns = ['name', 'phone', 'price', 'region', 'district']
        if not all(col in df.columns for col in required_columns):
            print('aaaaaaa')
            return JsonResponse({'status': 'error', 'message': 'Missing required columns in Excel file'}, status=400)
        
        created_leads = []
        
        for index, row in df.iterrows():
            try:
                region, _ = Region.objects.get_or_create(name=row['region'])
                district, _ = District.objects.get_or_create(name=row['district'], region=region)
                lead = Lead.objects.create(
                    name=row['name'],
                    phone=row['phone'],
                    price=row['price'],
                    district=district,
                    pole=request.user.leadpoles.first(), 
                    created_user=request.user
                )
                created_leads.append({
                    'id': lead.id,
                    'name': lead.name,
                    'phone': lead.phone,
                    'price': lead.price,
                    'district': lead.district.name,
                    'date': lead.date.strftime('%Y-%m-%d %H:%M'),
                    'created_user': {
                        'username': lead.created_user.username
                    },
                    'pole': lead.pole.id,
                    'company': lead.company,
                    'get_validity_period': lead.get_validity_period,  
                    'validity_period': lead.validity_period.strftime('%Y-%m-%d') if lead.validity_period else None
                })

            except Exception as e:
                print(f"Error creating lead from row {index}: {str(e)}")
                continue
        
        return JsonResponse({'status': 'success', 'data': created_leads})