from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import get_object_or_404


class IsContactOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return view.queryset.filter(pk=obj.id, sales_contact=request.user).exists() or request.user.role == "gestion"


class IsContactOrSupportOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return view.queryset.filter(pk=obj.id).filter(Q(contract__sales_contact=request.user) |
                                                                 Q(support=request.user)
                                                                 ).exists() or request.user.role == "gestion"


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "gestion"
