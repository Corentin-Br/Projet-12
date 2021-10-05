import datetime

from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import MyUserSerializer, ClientSerializer, EventSerializer, ContractSerializer
from accounts.models import MyUser
from clients.models import Contract, Client
from events.models import Event
from .permissions import IsContactOrReadOnly, IsContactOrSupportOrReadOnly, IsManager


class UserAPIViewSet(ModelViewSet):
    queryset = MyUser.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser, IsManager)
    serializer_class = MyUserSerializer

    def perform_update(self, serializer):
        """Add the password to the serializer data before saving it, if there is one."""
        if "password" in serializer.validated_data:
            serializer.save(password=serializer.validated_data["password"])
        else:
            serializer.save()

    def get_queryset(self):
        """Filter the queryset depending on given parameters."""
        queryset = super().get_queryset()
        email = self.request.query_params.get('email')
        role = self.request.query_params.get('role')
        if email is not None:
            queryset = queryset.filter(email=email)
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset


class ClientAPIViewSet(ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = (IsAuthenticated, IsContactOrReadOnly,)
    serializer_class = ClientSerializer

    def get_queryset(self):
        """Filter the queryset depending on given parameters."""
        queryset = super().get_queryset()
        email = self.request.query_params.get('email')
        company_name = self.request.query_params.get('company')
        sales_contact = self.request.query_params.get('contact')
        if email is not None:
            queryset = queryset.filter(email=email)
        if sales_contact is not None:
            queryset = queryset.filter(sales_contact__email=sales_contact)
        if company_name is not None:
            queryset = queryset.filter(company_name=company_name)
        return queryset


class EventAPIViewSet(ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = (IsAuthenticated, IsContactOrSupportOrReadOnly,)
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        """Create an event, turning the date and time into a datetime object."""
        data = request.data.copy()
        if "date_0" in request.data and "date_1" in request.data:
            data["date"] = merge_date_time(request.data["date_0"], request.data["date_1"])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Update an event, turning the date and time into a datetime object."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        if "date_0" in request.data and "date_1" in request.data:
            data["date"] = merge_date_time(request.data["date_0"], request.data["date_1"])
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        """Filter the queryset depending on given parameters."""
        queryset = super().get_queryset()
        client = self.request.query_params.get('client')
        support = self.request.query_params.get('support')
        contact = self.request.query_params.get('contact')
        if client is not None:
            queryset = queryset.filter(client__company_name=client)
        if contact is not None:
            queryset = queryset.filter(client__sales_contact__email=contact)
        if support is not None:
            queryset = queryset.filter(support__email=support)
        return queryset


class ContractAPIViewSet(ModelViewSet):
    queryset = Contract.objects.all()
    permission_classes = (IsAuthenticated, IsContactOrReadOnly,)
    serializer_class = ContractSerializer

    def create(self, request, *args, **kwargs):
        """Create a contract, turning the date and time into a datetime object."""
        data = request.data.copy()
        if "payment_due_0" in request.data and "payment_due_1" in request.data:
            data["payment_due"] = merge_date_time(request.data["payment_due_0"], request.data["payment_due_1"])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Update a contract, turning the date and time into a datetime object."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        if "payment_due_0" in request.data and "payment_due_1" in request.data:
            data["payment_due"] = merge_date_time(request.data["payment_due_0"], request.data["payment_due_1"])
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        """Filter the queryset depending on given parameters."""
        queryset = super().get_queryset()
        due = self.request.query_params.get('due')
        client = self.request.query_params.get('client')
        contact = self.request.query_params.get('contact')
        if due is not None and due.lower() == "true":
            queryset = queryset.filter(payment_due__lt=datetime.datetime.now())
        if contact is not None:
            queryset = queryset.filter(client__sales_contact__email=contact)
        if client is not None:
            queryset = queryset.filter(client__company_namel=client)
        return queryset


def merge_date_time(date, time):
    """Merge a date string and time string in a specific format into a single aware datetime object."""
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    time = datetime.datetime.strptime(time, "%H:%M:%S")
    time = datetime.time(hour=time.hour, minute=time.minute, second=time.second)
    return make_aware(datetime.datetime.combine(date, time))
