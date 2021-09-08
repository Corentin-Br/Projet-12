from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .serializers import MyUserSerializer, ClientSerializer, EventSerializer, ContractSerializer
from ..accounts.models import MyUser
from ..clients.models import Contract, Client
from ..events.models import Event
from .permissions import IsContactOrReadOnly, IsContactOrSupportOrReadOnly


class UserAPIViewSet(ModelViewSet):
    queryset = MyUser.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = MyUserSerializer


class ClientAPIViewSet(ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = (IsContactOrReadOnly,) #TODO: Is authenticated
    serializer_class = ClientSerializer


class EventAPIViewSet(ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = (IsContactOrSupportOrReadOnly,) #TODO: Is authenticated
    serializer_class = EventSerializer


class ContractAPIViewSet(ModelViewSet):
    queryset = Contract.objects.all()
    permission_classes = (IsContactOrReadOnly,) #TODO: Is authenticated
    serializer_class = ContractSerializer
