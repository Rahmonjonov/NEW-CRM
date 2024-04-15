from rest_framework import serializers
from board.models import Lead, LeadAction, Task, Telegram_user
from account.models import Company, Account


class AccountMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name']


class LeadSerializer(serializers.ModelSerializer):
    created_user = AccountMinSerializer(read_only=True)

    class Meta:
        model = Lead
        fields = '__all__'


class LeadActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadAction
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class Telegram_userSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telegram_user
        fields = '__all__'
