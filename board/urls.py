from django.urls import path

from .views import (Board, create_lead, change_lead_status, lead_finished, lead_losed, edit_lead,
                    get_lead_count, create_lead_by_tg, telegram_bot_get_company, telegram_bot_add_phone,
                    telegram_bot_add_company,
                    telegram_bot_add_company_address, telegram_bot_add_name, add_pole, edit_pole, check_pole_can_delete,
                    delete_pole, export_excel, redirect_view, Redirect_class, NewUrlRedirect_class,
                    EditUrlRedirect_class, PublicNoteForm_class, NewFormRedirect_class, ShowFormResults_class,
                    AddShopping_class, EditShopping_class, delete_simple_redirect, delete_form_redirect, InstruktsyaList, instruktsya_add, instruktsya_list_detail)

urlpatterns = [
    path("", Board.as_view(), name="board"),
    path("instruktsya/", InstruktsyaList.as_view(), name="instruktsya"),
    path("instruktsya_list_detail/<int:id>", instruktsya_list_detail, name="instruktsya_list_detail"),
    path("instruktsya_add/", instruktsya_add, name="instruktsya_add"),
    path("create_lead/", create_lead),
    path("change_lead_status/", change_lead_status),
    path("lead_finished/", lead_finished),
    path("lead_losed/", lead_losed),
    path("edit_lead/", edit_lead),
    path("add_pole/", add_pole, name="add_pole"),
    path("edit_pole/", edit_pole, name="edit_pole"),
    path("check_can_delete_pole/", check_pole_can_delete, name="check_pole_can_delete"),
    path("delete_pole/", delete_pole, name="delete_pole"),
    path("create_lead_by_tg/", create_lead_by_tg),
    path("telegram_bot_get_company/", telegram_bot_get_company),
    path("telegram_bot_add_name/", telegram_bot_add_name),
    path("telegram_bot_add_phone/", telegram_bot_add_phone),
    path("telegram_bot_add_company/", telegram_bot_add_company),
    path("telegram_bot_add_company_address/", telegram_bot_add_company_address),
    path("get_lead_count/", get_lead_count, name='get_lead_count'),

    path('export_excel/', export_excel, name='export_excel'),

    path('shopping/add/<int:pk>/', AddShopping_class.as_view(), name='AddShopping_class'),
    path('shopping/edit/<int:pk>/<int:shop_pk>/', EditShopping_class.as_view(), name='EditShopping_class'),

]

urlpatterns_for_redirect = [

    path('redirects/social/', redirect_view, name='redirect_view'),
    path('redirects/form/', PublicNoteForm_class.as_view(), name='PublicNoteForm_class'),

    path('redirect/', Redirect_class.as_view(), name='redirect_list'),
    path('redirect/add/', NewUrlRedirect_class.as_view(), name='NewUrlRedirect_class'),
    path('redirect/edit/<int:pk>/', EditUrlRedirect_class.as_view(), name='EditUrlRedirect_class'),

    path('redirect/form/add/', NewFormRedirect_class.as_view(), name='NewFormRedirect_class'),

    path('redirect/form/show/<int:pk>/', ShowFormResults_class.as_view(), name='ShowFormResults_class'),

    path('redirect/simple/delete/<int:pk>/', delete_simple_redirect, name='delete_simple_redirect'),
    path('redirect/form/delete/<int:pk>/', delete_form_redirect, name='delete_form_redirect'),
]
