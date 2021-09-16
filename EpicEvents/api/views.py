from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import MyUserSerializer, ClientSerializer, EventSerializer, ContractSerializer
from accounts.models import MyUser
from clients.models import Contract, Client
from events.models import Event
from .permissions import IsContactOrReadOnly, IsContactOrSupportOrReadOnly, IsManager


class UserAPIViewSet(ModelViewSet):
    queryset = MyUser.objects.all()
    permission_classes = (IsAdminUser, IsManager)
    serializer_class = MyUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def perform_update(self, serializer):
        if "password" in serializer.validated_data:
            serializer.save(password=serializer.validated_data["password"])
        else:
            serializer.save()


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
