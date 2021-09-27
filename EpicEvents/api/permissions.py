from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import get_object_or_404

import api.views


class IsContactOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ("sales", "support", "gestion")
        return request.user.role in ("sales", "gestion")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ("sales", "support", "gestion")
        return view.queryset.filter(pk=obj.id, sales_contact=request.user).exists() or \
            (view.queryset.filter(pk=obj.id, sales_contact__isnull=True).exists() and request.user.role == "sales") or \
            request.user.role == "gestion"


class IsContactOrSupportOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.role in ("sales", "gestion")
        return request.user.role in ("sales", "gestion", "support")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ("sales", "support", "gestion")
        return view.queryset.filter(pk=obj.id, support=request.user).exists() or request.user.role == "gestion"


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "gestion"
