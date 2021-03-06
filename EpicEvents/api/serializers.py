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
        read_only_fields = ['id']

    def create(self, validated_data):
        """Use the create_user method of the user to create it.

        It ensures that it follows the model rules."""
        return MyUser.objects.create_user(**validated_data)

    def save(self, **kwargs):
        """Save the model. If a password is given, turn it into a proper password."""
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
        read_only_fields = ['id', 'date_created', 'date_updated']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'client', 'date_created', 'date_updated', 'support', 'contract', 'attendees', 'date', 'notes']
        read_only_fields = ['id', 'date_created', 'date_updated']

    def validate(self, data):
        """Ensure that the client and the client in the contract are the samen, in addition to all usual checks."""
        if data["contract"].client != data["client"]:
            raise serializers.ValidationError("The client must be the same for the event and the contract!")
        return super().validate(data)


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'sales_contact', 'client', 'date_created', 'date_updated', 'status', 'amount', 'payment_due']
        read_only_fields = ['id', 'date_created', 'date_updated']


