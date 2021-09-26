from django.contrib.auth.hashers import make_password
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
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'role', 'events', 'clients', 'contracts']

    def create(self, validated_data):
        return MyUser.objects.create_user(**validated_data)

    def save(self, **kwargs):
        if "password" in kwargs:
            kwargs["password"] = make_password(kwargs["password"])
        self.instance = super().save(**kwargs)
        return self.instance


class ClientSerializer(serializers.ModelSerializer):
    events = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    contracts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'mobile_number', 'company_name',
                  'date_created', 'date_updated', 'sales_contact', 'events', 'contracts']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'client', 'date_created', 'date_updated', 'support', 'contract', 'attendees', 'date', 'notes']

    def validate(self, data):
        if data["contract"].client != data["client"]:
            raise serializers.ValidationError("The client must be the same for the event and the contract!")
        return super().validate(data)

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'sales_contact', 'client', 'date_created', 'date_updated', 'status', 'amount', 'payment_due']


