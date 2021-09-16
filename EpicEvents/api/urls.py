from django.urls import path, include
# from rest_framework_simplejwt.views import TokenObtainPairView

from .views import ClientAPIViewSet, ContractAPIViewSet, UserAPIViewSet, EventAPIViewSet

user_change = UserAPIViewSet.as_view(
    {
        'post': 'partial_update',
    }
)

urlpatterns = [
    path('users/<int:pk>', user_change, name="user_change"),
    path('api-auth/', include('rest_framework.urls'))
    ]