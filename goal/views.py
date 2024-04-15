import json

from django.contrib.auth.mixins import AccessMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from account.models import Account
from board.models import Lead
from goal.models import Goal


def get_users(request):
    users = Account.objects.filter(company=request.user.company)
    data = []
    for user in users:
        dt = {
            "id": user.id
        }
        data.append(dt)

    return JsonResponse(data, safe=False)


def add_goals(request):
    if request.method == "POST":
        data = request.POST.get('data')
        data = json.loads(data)

        for dt in data:
            user = dt['user']
            goal_type = dt['gaol_type']
            savdo = dt['savdo']
            mijoz = dt['mijoz']
            yil = dt['yil']
            oy = dt['oy']
            if goal_type == "1":
                type = "Yillik"
                oy = 0
            else:
                oy = oy + 1
                type = "Oylik"

            if savdo == "":
                savdo = 0
            else:
                savdo = int(savdo)

            if mijoz == "":
                mijoz = 0
            else:
                mijoz = int(mijoz)
            detail, created = Goal.objects.get_or_create(
                user_id=user,
                type=type, yil=yil, oy=oy, defaults={"savdo": savdo, "mijoz_soni": mijoz}

            )
            if not created:
                detail.savdo = savdo
                detail.mijoz_soni = mijoz
                detail.save()

        return JsonResponse({"status": 1})
    else:
        return JsonResponse({"status": 0})


def get_goals(request):
    goal_type = request.GET.get("goal_type")
    oy = request.GET.get("oy")
    yil = request.GET.get("yil")
    queryset = Goal.objects.filter(user__company=request.user.company, yil=yil)
    if goal_type == "1":
        goals = queryset.filter(type="Yillik")
    else:
        goals = queryset.filter(type="Oylik", oy=int(oy) + 1)

    data = []
    for goal in goals:
        dt = {
            "user": goal.user.id,
            "savdo": goal.savdo,
            "mijoz": goal.mijoz_soni
        }
        data.append(dt)
    return JsonResponse(data, safe=False)


def get_goal_table(request):
    goal_type = request.GET.get("goal_type")
    goal_data_type = request.GET.get("goal_data_type")
    sana = request.GET.get("sana")
    data = []
    if sana is not None:
        date = str(sana).split("-")
        yil = int(date[0])
        oy = int(date[1])
        if goal_type == "Oylik":
            goals = Goal.objects.filter(type=goal_type, yil=yil, oy=oy, user__company=request.user.company)
            leads = Lead.objects.filter(is_active=True, finishedDate__year=yil, finishedDate__month=oy, status=5, created_user__company=request.user.company)
        else:
            goals = Goal.objects.filter(type=goal_type, yil=yil, user__company=request.user.company)
            leads = Lead.objects.filter(is_active=True, finishedDate__year=yil, status=5, created_user__company=request.user.company)
        for goal in goals:
            if goal_data_type == "Savdo":
                maqsad = goal.savdo
                bajardi = leads.filter(created_user=goal.user).aggregate(total=Sum("finishedPrice")).get("total")
                if bajardi is None:
                    bajardi = 0
            else:
                maqsad = goal.mijoz_soni
                bajardi = leads.filter(created_user=goal.user).count()
            maqsad = maqsad if maqsad !=0 else 1
            foiz = int(bajardi * 100 / maqsad)
            dt = {
                "user": goal.user.first_name + " " + goal.user.last_name,
                "bajardi": bajardi,
                "foiz": foiz,
                "maqsad": maqsad,
                "yil": yil,
                "oy": oy - 1
            }
            data.append(dt)
    return JsonResponse(data, safe=False)

from main.models import Company
class Maqsad(TemplateView, AccessMixin):
    login_url = '/login'
    template_name = 'goal.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_director:
            return redirect('home')
        # if not request.user.company.active:
        #     return redirect('cabinet')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        super(Maqsad, self).get_context_data(**kwargs)
        users = Account.objects.filter(company=self.request.user.company)
        context = {
            "maqsad": "active",
            "users": users
        }
        context['company'] = Company.objects.get(id=self.request.user.company.id)
        return context
