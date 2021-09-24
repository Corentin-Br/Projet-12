from django.urls import path, include
# from rest_framework_simplejwt.views import TokenObtainPairView

from .views import ClientAPIViewSet, ContractAPIViewSet, UserAPIViewSet, EventAPIViewSet

user_change = UserAPIViewSet.as_view(
    {
        'post': 'partial_update',
    }
)

user_create = UserAPIViewSet.as_view(
    {
        'post': 'create',
    }
)

user_list = UserAPIViewSet.as_view(
    {
        'get': 'list',
        'post': 'list'
    }
)

user_find = UserAPIViewSet.as_view(
    {
        'get': 'retrieve'
    }
)

user_delete = UserAPIViewSet.as_view(
    {
        'post': 'destroy'
    }
)

client_change = ClientAPIViewSet.as_view(
    {
        'post': 'partial_update',
    }
)

client_create = ClientAPIViewSet.as_view(
    {
        'post': 'create',
    }
)

client_list = ClientAPIViewSet.as_view(
    {
        'get': 'list',
        'post': 'list'
    }
)

client_find = ClientAPIViewSet.as_view(
    {
        'get': 'retrieve'
    }
)

client_delete = ClientAPIViewSet.as_view(
    {
        'post': 'destroy'
    }
)

contract_change = ContractAPIViewSet.as_view(
    {
        'post': 'partial_update',
    }
)

contract_create = ContractAPIViewSet.as_view(
    {
        'post': 'create',
    }
)

contract_list = ContractAPIViewSet.as_view(
    {
        'get': 'list',
        'post': 'list'
    }
)

contract_find = ContractAPIViewSet.as_view(
    {
        'get': 'retrieve'
    }
)

contract_delete = ContractAPIViewSet.as_view(
    {
        'post': 'destroy'
    }
)

event_change = EventAPIViewSet.as_view(
    {
        'post': 'partial_update',
    }
)

event_create = EventAPIViewSet.as_view(
    {
        'post': 'create',
    }
)

event_list = EventAPIViewSet.as_view(
    {
        'get': 'list',
        'post': 'list'
    }
)

event_find = EventAPIViewSet.as_view(
    {
        'get': 'retrieve'
    }
)

event_delete = EventAPIViewSet.as_view(
    {
        'post': 'destroy'
    }
)

urlpatterns = [
    path('users/<int:pk>/edit', user_change, name="user_change"),
    path('users/create/', user_create, name="user_create"),
    path('users/list/', user_list, name="user_list"),
    path('users/<int:pk>/', user_find, name="user_find"),
    path('users/delete/<int:pk>', user_delete, name="user_delete"),
    path('contract/<int:pk>/edit', contract_change, name="contract_change"),
    path('contracts/create/', contract_create, name="contract_create"),
    path('contracts/list/', contract_list, name="contract_list"),
    path('contracts/<int:pk>/', contract_find, name="contract_find"),
    path('contracts/delete/<int:pk>', contract_delete, name="contract_delete"),
    path('events/<int:pk>/edit', event_change, name="event_change"),
    path('events/create/', event_create, name="event_create"),
    path('events/list/', event_list, name="event_list"),
    path('events/<int:pk>/', event_find, name="event_find"),
    path('events/delete/<int:pk>', event_delete, name="event_delete"),
    path('clients/<int:pk>/edit', client_change, name="client_change"),
    path('clients/create/', client_create, name="client_create"),
    path('clients/list/', client_list, name="client_list"),
    path('clients/<int:pk>/', client_find, name="client_find"),
    path('clients/delete/<int:pk>', client_delete, name="client_delete"),
    path('api-auth/', include('rest_framework.urls'))
    ]