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

# user_find = UserAPIViewSet.as_view(
#     {
#         'get': 'retrieve'
#     }
# )

user_delete = UserAPIViewSet.as_view(
    {
        'post': 'destroy'
    }
)

urlpatterns = [
    path('users/<int:pk>/', user_change, name="user_change"),
    path('users/create/', user_create, name="user_create"),
    path('users/list/', user_list, name="user_list"),
    # path('users/<int:pk>/', user_find, name="user_find"),
    path('users/delete/<int:pk>', user_delete, name="user_delete"),
    path('api-auth/', include('rest_framework.urls'))
    ]