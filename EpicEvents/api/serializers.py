from rest_framework import serializers
from accounts.models import MyUser
from clients.models import Contract, Client
from events.models import Event


class MyUserSerializer(serializers.ModelSerializer):
    events = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    clients = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    contracts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ['email', 'first_name', 'last_name', 'password', 'role', 'events', 'clients', 'contracts']

    def create(self, validated_data):
        return MyUser.objects.create_user(**validated_data)

    def save(self, **kwargs):
        self.instance = super().save(**kwargs)
        if "password" in kwargs:
            self.instance.set_password(kwargs["password"])
            self.instance.save()
        return self.instance


class ClientSerializer(serializers.ModelSerializer):
    events = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    contracts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'mobile_number', 'company_name',
                  'date_created', 'date_updated', 'sales_contact']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['client', 'date_created', 'date_updated', 'support', 'contract', 'attendees', 'date', 'notes']


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['sales_contact', 'client', 'date_created', 'date_updated', 'status', 'amount', 'payment_due']
