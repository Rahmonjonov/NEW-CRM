from django.urls import path
from .views import *

urlpatterns = [
    path("",Maqsad.as_view(),name="maqsad"),
    path('get_users',get_users,name="get_users"),
    path('add_goal',add_goals,name="add_goal"),
    path('get_goal',get_goals,name="get_goal"),
    path('get_goal_table',get_goal_table,name="get_goal_table"),
]

